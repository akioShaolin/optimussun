"""Estado e cálculo da matriz de compatibilidade, independentes da GUI."""

from dataclasses import dataclass, replace
import math

from .engine import compare_operating_current_modes
from .models import CompatibilityOptions, CompatibilityResult, EquipmentSummary
from .repository import load_inverter, load_module


@dataclass(frozen=True)
class InverterSelection:
    key: int
    equipment: EquipmentSummary | None
    display_label: str
    overload_mode: str = "registered"
    custom_overload_percent: float | None = None

    @property
    def associated(self):
        return self.equipment is not None and self.equipment.database_id is not None

    def compatibility_options(self, base_options=None):
        base = base_options or CompatibilityOptions()
        custom = (
            self.custom_overload_percent
            if self.overload_mode == "custom"
            else None
        )
        return replace(base, custom_overload_percent=custom)


@dataclass(frozen=True)
class ModuleSelection:
    key: int
    equipment: EquipmentSummary | None
    display_model: str
    nominal_power_w: float | None

    @property
    def associated(self):
        return self.equipment is not None and self.equipment.database_id is not None


@dataclass(frozen=True)
class MatrixCellResult:
    normal: CompatibilityResult
    ignored: CompatibilityResult

    @property
    def uses_ignored_result(self):
        return self.ignored.valid and self.ignored.quantity > self.normal.quantity

    @property
    def display_result(self):
        return self.ignored if self.uses_ignored_result else self.normal


@dataclass(frozen=True)
class ImportedCellValue:
    quantity: int | None
    dc_power_kw: float | None
    overload_percent: float | None
    valid: bool


@dataclass(frozen=True)
class ImportedCellResult:
    imported_value: ImportedCellValue

    @property
    def uses_ignored_result(self):
        return False

    @property
    def display_result(self):
        return self.imported_value


@dataclass(frozen=True)
class MatrixCalculation:
    inverters: tuple[InverterSelection, ...]
    modules: tuple[ModuleSelection, ...]
    cells: dict[tuple[int, int], MatrixCellResult | ImportedCellResult]
    source: str = "calculated"

    def cell(self, inverter_key, module_key):
        return self.cells[(inverter_key, module_key)]


class CompatibilityMatrix:
    """Mantém seleções e produz um snapshot calculado da matriz."""

    def __init__(self):
        self.inverters = []
        self.modules = []
        self._next_key = 1

    def _key(self):
        value = self._next_key
        self._next_key += 1
        return value

    def add_inverter(self, equipment, display_label=None):
        selection = InverterSelection(
            self._key(), equipment, display_label or equipment.model
        )
        self.inverters.append(selection)
        return selection

    def add_imported_inverter(self, display_label, equipment=None):
        selection = InverterSelection(self._key(), equipment, display_label)
        self.inverters.append(selection)
        return selection

    def remove_inverter(self, key):
        self.inverters = [item for item in self.inverters if item.key != key]

    def rename_inverter(self, key, display_label):
        label = display_label.strip()
        if not label:
            raise ValueError("O texto exibido do inversor não pode ficar vazio.")
        for position, item in enumerate(self.inverters):
            if item.key == key:
                self.inverters[position] = replace(item, display_label=label)
                return
        raise KeyError(key)

    def configure_inverter_overload(self, key, mode, custom_percent=None):
        if mode not in {"registered", "custom"}:
            raise ValueError(f"Modo de sobrecarga desconhecido: {mode}")
        if mode == "custom":
            if (
                custom_percent is None
                or not isinstance(custom_percent, (int, float))
                or not math.isfinite(custom_percent)
                or custom_percent < 0
            ):
                raise ValueError("Informe uma sobrecarga personalizada não negativa.")
            custom_percent = float(custom_percent)
        else:
            custom_percent = None
        for position, item in enumerate(self.inverters):
            if item.key == key:
                self.inverters[position] = replace(
                    item,
                    overload_mode=mode,
                    custom_overload_percent=custom_percent,
                )
                return
        raise KeyError(key)

    def associate_inverter(self, key, equipment):
        for position, item in enumerate(self.inverters):
            if item.key == key:
                self.inverters[position] = replace(
                    item,
                    equipment=equipment,
                    overload_mode="registered",
                    custom_overload_percent=None,
                )
                return
        raise KeyError(key)

    def sorted_inverters(self):
        return tuple(
            sorted(
                self.inverters,
                key=lambda item: (item.display_label.casefold(), item.key),
            )
        )

    def add_module(self, equipment):
        selection = ModuleSelection(
            self._key(), equipment, equipment.model, equipment.nominal_power_w
        )
        self.modules.append(selection)
        return selection


    def add_imported_module(self, display_model, nominal_power_w, equipment=None):
        model = display_model.strip()
        power = None if nominal_power_w is None else float(nominal_power_w)
        if not model:
            raise ValueError("O modelo exibido do módulo não pode ficar vazio.")
        if power is not None and (not math.isfinite(power) or power <= 0):
            raise ValueError("A potência nominal do módulo deve ser positiva.")
        selection = ModuleSelection(
            self._key(), equipment, model, power
        )
        self.modules.append(selection)
        return selection

    def associate_module(self, key, equipment):
        for position, item in enumerate(self.modules):
            if item.key == key:
                self.modules[position] = replace(item, equipment=equipment)
                return
        raise KeyError(key)

    def remove_module(self, key):
        self.modules = [item for item in self.modules if item.key != key]

    def move_module(self, key, destination):
        index = next(
            (position for position, item in enumerate(self.modules) if item.key == key),
            None,
        )
        if index is None:
            raise KeyError(key)
        if destination == "left":
            target = max(0, index - 1)
        elif destination == "right":
            target = min(len(self.modules) - 1, index + 1)
        elif destination == "start":
            target = 0
        elif destination == "end":
            target = len(self.modules) - 1
        else:
            raise ValueError(f"Destino desconhecido: {destination}")
        item = self.modules.pop(index)
        self.modules.insert(target, item)

    def calculate(self, connection, options=None):
        if not self.inverters or not self.modules:
            raise ValueError("Adicione ao menos um inversor e um módulo.")
        options = options or CompatibilityOptions()
        inverter_cache = {}
        module_cache = {}
        cells = {}
        ordered_inverters = self.sorted_inverters()
        ordered_modules = tuple(self.modules)
        for inverter_selection in ordered_inverters:
            if not inverter_selection.associated:
                raise ValueError(
                    f"Inversor não associado: {inverter_selection.display_label}"
                )
            inverter_id = inverter_selection.equipment.database_id
            if inverter_id not in inverter_cache:
                inverter_cache[inverter_id] = load_inverter(connection, inverter_id)
            inverter = inverter_cache[inverter_id]
            row_options = inverter_selection.compatibility_options(options)
            for module_selection in ordered_modules:
                if not module_selection.associated:
                    raise ValueError(
                        f"Módulo não associado: {module_selection.display_model}"
                    )
                module_id = module_selection.equipment.database_id
                if module_id not in module_cache:
                    module_cache[module_id] = load_module(connection, module_id)
                module = module_cache[module_id]
                normal, ignored = compare_operating_current_modes(
                    inverter, module, row_options
                )
                cells[(inverter_selection.key, module_selection.key)] = (
                    MatrixCellResult(normal, ignored)
                )
        return MatrixCalculation(ordered_inverters, ordered_modules, cells)

    def snapshot_with_cells(self, calculation):
        """Reaplica seleção/ordem aos valores existentes sem recalcular."""
        inverters = self.sorted_inverters()
        modules = tuple(self.modules)
        required = {(row.key, module.key) for row in inverters for module in modules}
        if not required.issubset(calculation.cells):
            raise ValueError("A seleção possui células ainda não calculadas.")
        cells = {key: calculation.cells[key] for key in required}
        return MatrixCalculation(inverters, modules, cells, calculation.source)
