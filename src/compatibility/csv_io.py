"""Importação e exportação CSV da matriz de compatibilidade."""

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from .matrix import (
    CompatibilityMatrix,
    ImportedCellResult,
    ImportedCellValue,
    MatrixCalculation,
)
from .models import LimitingFactor


class CSVFormatError(ValueError):
    """Indica que um CSV não segue a estrutura da matriz do Optimus Sun."""


@dataclass(frozen=True)
class ImportedMatrix:
    matrix: CompatibilityMatrix
    calculation: MatrixCalculation


def _format_number(value, max_places=6):
    text = f"{value:.{max_places}f}".rstrip("0").rstrip(".")
    return text.replace(".", ",") or "0"


def _display_values(cell):
    result = cell.display_result
    if isinstance(cell, ImportedCellResult):
        invalid = not result.valid
    else:
        invalid = result.limiting_factor == LimitingFactor.MISSING_DATA
    if invalid:
        return "N/D", "N/D", "N/D"
    return (
        str(result.quantity),
        _format_number(result.dc_power_kw),
        f"{_format_number(result.overload_percent)}%",
    )


def export_matrix_csv(calculation, path):
    """Exporta o snapshot atual usando exclusivamente seu display_result."""
    target = Path(path)
    with target.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream, delimiter=";", lineterminator="\n")
        header_models = ["Inversor"]
        header_power = [""]
        header_fields = ["Inversor"]
        for module in calculation.modules:
            header_models.extend([module.display_model] * 3)
            power = _format_number(module.nominal_power_w)
            header_power.extend([power] * 3)
            header_fields.extend(
                ["Quantidade de módulos", "Potência (kW)", "Sobrecarga (%)"]
            )
        writer.writerow(header_models)
        writer.writerow(header_power)
        writer.writerow(header_fields)
        for inverter in calculation.inverters:
            row = [inverter.display_label]
            for module in calculation.modules:
                row.extend(_display_values(calculation.cell(inverter.key, module.key)))
            writer.writerow(row)


def _read_rows(path):
    data = Path(path).read_bytes()
    last_error = None
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError as error:
            last_error = error
    else:
        raise CSVFormatError(f"Não foi possível decodificar o arquivo: {last_error}")
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=";,\t")
        delimiter = dialect.delimiter
    except csv.Error:
        delimiter = ";"
    return list(csv.reader(text.splitlines(), delimiter=delimiter))


def _number(value, line, column, percent=False):
    text = value.strip()
    if percent:
        text = text.removesuffix("%").strip()
    normalized = text.replace(" ", "")
    if "," in normalized and "." in normalized:
        if normalized.rfind(",") > normalized.rfind("."):
            normalized = normalized.replace(".", "").replace(",", ".")
        else:
            normalized = normalized.replace(",", "")
    else:
        normalized = normalized.replace(",", ".")
    try:
        number = float(normalized)
    except ValueError as error:
        kind = "percentual" if percent else "número"
        raise CSVFormatError(
            f"Linha {line}, coluna {column}: {kind} inválido: {value!r}."
        ) from error
    if not math.isfinite(number):
        raise CSVFormatError(
            f"Linha {line}, coluna {column}: valor não finito: {value!r}."
        )
    return number


def _exact_map(equipment):
    by_model = {}
    duplicates = set()
    for item in equipment:
        if item.model in by_model:
            duplicates.add(item.model)
        else:
            by_model[item.model] = item
    for model in duplicates:
        by_model.pop(model, None)
    return by_model


def import_matrix_csv(path, active_inverters=(), active_modules=()):
    """Carrega valores sem executar o motor e associa modelos por igualdade exata."""
    rows = _read_rows(path)
    if len(rows) < 4:
        raise CSVFormatError("O arquivo deve possuir três cabeçalhos e ao menos uma linha.")
    width = len(rows[0])
    if width < 4 or (width - 1) % 3:
        raise CSVFormatError("As colunas após Inversor devem formar grupos de três.")
    for line, row in enumerate(rows, 1):
        if len(row) != width:
            raise CSVFormatError(
                f"Linha {line}: esperado {width} colunas, encontrado {len(row)}."
            )
    if rows[0][0].strip().casefold() != "inversor":
        raise CSVFormatError("Linha 1, coluna 1 deve conter 'Inversor'.")
    if rows[2][0].strip().casefold() != "inversor":
        raise CSVFormatError("Linha 3, coluna 1 deve conter 'Inversor'.")
    expected = ("quantidade de módulos", "potência (kw)", "sobrecarga (%)")
    inverter_map = _exact_map(active_inverters)
    module_map = _exact_map(active_modules)
    matrix = CompatibilityMatrix()
    module_selections = []
    for start in range(1, width, 3):
        models = [rows[0][start + offset].strip() for offset in range(3)]
        if not models[0] or len(set(models)) != 1:
            raise CSVFormatError(
                f"Cabeçalho do módulo nas colunas {start + 1}–{start + 3} é inconsistente."
            )
        powers = [
            _number(rows[1][start + offset], 2, start + offset + 1)
            for offset in range(3)
        ]
        if any(abs(value - powers[0]) > 1e-9 for value in powers[1:]):
            raise CSVFormatError(
                f"Potência do módulo {models[0]!r} não se repete nas três colunas."
            )
        if powers[0] <= 0:
            raise CSVFormatError(
                f"Potência do módulo {models[0]!r} deve ser positiva."
            )
        fields = tuple(rows[2][start + offset].strip().casefold() for offset in range(3))
        if fields != expected:
            raise CSVFormatError(
                f"Cabeçalhos inválidos para o módulo {models[0]!r}."
            )
        module_selections.append(
            matrix.add_imported_module(
                models[0], powers[0], module_map.get(models[0])
            )
        )

    cells = {}
    inverter_selections = []
    for line_number, row in enumerate(rows[3:], 4):
        label = row[0].strip()
        if not label:
            raise CSVFormatError(f"Linha {line_number}: texto do inversor vazio.")
        inverter = matrix.add_imported_inverter(label, inverter_map.get(label))
        inverter_selections.append(inverter)
        for module_index, module in enumerate(module_selections):
            start = 1 + module_index * 3
            values = [row[start + offset].strip() for offset in range(3)]
            if all(value.casefold() == "n/d" for value in values):
                imported = ImportedCellValue(None, None, None, False)
            elif any(value.casefold() == "n/d" for value in values):
                raise CSVFormatError(
                    f"Linha {line_number}, módulo {module.display_model!r}: "
                    "N/D deve ocupar as três células."
                )
            else:
                quantity_value = _number(values[0], line_number, start + 1)
                if not quantity_value.is_integer() or quantity_value < 0:
                    raise CSVFormatError(
                        f"Linha {line_number}, módulo {module.display_model!r}: "
                        "quantidade deve ser um inteiro não negativo."
                    )
                power = _number(values[1], line_number, start + 2)
                overload = _number(values[2], line_number, start + 3, percent=True)
                if power < 0:
                    raise CSVFormatError(
                        f"Linha {line_number}, módulo {module.display_model!r}: "
                        "potência deve ser não negativa."
                    )
                imported = ImportedCellValue(
                    int(quantity_value), power, overload, True
                )
            cells[(inverter.key, module.key)] = ImportedCellResult(imported)
    calculation = MatrixCalculation(
        tuple(inverter_selections), tuple(module_selections), cells, "imported"
    )
    return ImportedMatrix(matrix, calculation)
