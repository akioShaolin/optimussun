# -*- coding: utf-8 -*-
"""
Interface gráfica com Tkinter para gerenciar todas as tabelas
do banco de dados SQLite optimus_sun.db.
Baseado no script anterior e seguindo o mesmo modelo.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

DATABASE_NAME = "optimus_sun.db"

class DatabaseManager:
    """Gerencia a conexão e operações no banco de dados SQLite."""
    def __init__(self, db_name):
        self.db_name = db_name
        if not os.path.exists(self.db_name):
            messagebox.showerror("Erro de Banco de Dados", f"O arquivo de banco de dados '\'{self.db_name}\' não foi encontrado.")
            raise FileNotFoundError(f"Database file '\'{self.db_name}\' not found.")

    def _connect(self):
        """Estabelece conexão com o banco de dados."""
        try:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row # Retorna dicionários em vez de tuplas
            conn.execute("PRAGMA foreign_keys = ON") # Habilita chaves estrangeiras
            return conn
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Conexão", f"Erro ao conectar ao banco de dados: {e}")
            return None

    def execute_query(self, query, params=()):
        """Executa uma query que não retorna dados (INSERT, UPDATE, DELETE)."""
        conn = self._connect()
        if not conn:
            return False, None # Retorna False e None em caso de falha na conexão
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            last_id = cursor.lastrowid
            conn.commit()
            return True, last_id # Retorna True e o ID inserido (se aplicável)
        except sqlite3.Error as e:
            conn.rollback()
            # Evitar exibir a query completa em produção real por segurança
            messagebox.showerror("Erro de Query", f"Erro ao executar operação no banco: {e}")
            # print(f"Query: {query}\nParams: {params}") # Para debug
            return False, None # Retorna False e None em caso de erro
        finally:
            if conn:
                conn.close()

    def fetch_all(self, query, params=()):
        """Executa uma query e retorna todos os resultados."""
        conn = self._connect()
        if not conn:
            return []
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            # Converte para lista de dicionários para consistência
            return [dict(row) for row in results]
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Fetch", f"Erro ao buscar dados: {e}")
            # print(f"Query: {query}\nParams: {params}") # Para debug
            return []
        finally:
            if conn:
                conn.close()

    def fetch_one(self, query, params=()):
        """Executa uma query e retorna um único resultado."""
        conn = self._connect()
        if not conn:
            return None
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return dict(result) if result else None # Converte para dicionário
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Fetch", f"Erro ao buscar dado: {e}")
            # print(f"Query: {query}\nParams: {params}") # Para debug
            return None
        finally:
            if conn:
                conn.close()

    def get_table_columns(self, table_name):
        """Obtém os nomes das colunas de uma tabela."""
        query = f"PRAGMA table_info({table_name})"
        conn = self._connect()
        if not conn:
            return []
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            # Retorna a lista de nomes das colunas (índice 1 da tupla retornada por PRAGMA)
            columns = [row[1] for row in cursor.fetchall()]
            return columns
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao obter colunas da tabela {table_name}: {e}")
            return []
        finally:
            if conn:
                conn.close()

    # --- Generic CRUD --- 
    # (Pode ser usado como base, mas operações específicas são melhores para validação e FKs)
    def add_record(self, table_name, data):
        """Adiciona um novo registro genérico."""
        fields = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"
        success, last_id = self.execute_query(query, tuple(data.values()))
        return success

    def update_record(self, table_name, record_id, data):
        """Atualiza um registro genérico existente."""
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE ID = ?"
        params = tuple(data.values()) + (record_id,)
        success, _ = self.execute_query(query, params)
        return success

    def delete_record(self, table_name, record_id):
        """Deleta um registro genérico."""
        query = f"DELETE FROM {table_name} WHERE ID = ?"
        success, _ = self.execute_query(query, (record_id,))
        return success

    # --- Manufacturer Operations ---
    def get_manufacturers(self):
        return self.fetch_all("SELECT * FROM manufacturer ORDER BY NAME")

    def add_manufacturer(self, data):
        return self.add_record("manufacturer", data)

    def update_manufacturer(self, manufacturer_id, data):
        return self.update_record("manufacturer", manufacturer_id, data)

    def delete_manufacturer(self, manufacturer_id):
        # Verificar se há inversores ou módulos associados antes de deletar?
        # Por enquanto, permite deletar, mas pode dar erro de FK se houver dependências
        # e PRAGMA foreign_keys=ON estiver ativo.
        return self.delete_record("manufacturer", manufacturer_id)

    # --- Inverter Operations ---
    def get_inverters(self):
        query = """
            SELECT i.*, m.NAME as MANUFACTURER_NAME 
            FROM inverter i
            LEFT JOIN manufacturer m ON i.MANUFACTURER_ID = m.ID
            ORDER BY i.MODEL
        """
        return self.fetch_all(query)

    def add_inverter(self, data):
        return self.add_record("inverter", data)

    def update_inverter(self, inverter_id, data):
        return self.update_record("inverter", inverter_id, data)

    def delete_inverter(self, inverter_id):
        # ON DELETE CASCADE cuidará dos filhos (mppt, system, comm, output_mode)
        return self.delete_record("inverter", inverter_id)

    # --- MPPT Operations ---
    def get_mppts_for_inverter(self, inverter_id):
        query = "SELECT * FROM mppt WHERE INVERTER_ID = ? ORDER BY MPPT_INDEX"
        return self.fetch_all(query, (inverter_id,))

    def add_mppt(self, data):
        return self.add_record("mppt", data)

    def update_mppt(self, mppt_id, data):
        return self.update_record("mppt", mppt_id, data)

    def delete_mppt(self, mppt_id):
        return self.delete_record("mppt", mppt_id)

    # --- Inverter System Operations ---
    def get_systems_for_inverter(self, inverter_id):
        query = "SELECT * FROM inverter_system WHERE INVERTER_ID = ? ORDER BY ID"
        return self.fetch_all(query, (inverter_id,))

    def add_system(self, data):
        return self.add_record("inverter_system", data)

    def update_system(self, system_id, data):
        # Precisa remover INVERTER_ID dos dados se for atualizar?
        # A princípio não, pois o ID do sistema é único.
        return self.update_record("inverter_system", system_id, data)

    def delete_system(self, system_id):
        return self.delete_record("inverter_system", system_id)

    # --- Inverter Communication Operations ---
    def get_communications_for_inverter(self, inverter_id):
        query = "SELECT * FROM inverter_communication WHERE INVERTER_ID = ? ORDER BY ID"
        return self.fetch_all(query, (inverter_id,))

    def add_communication(self, data):
        return self.add_record("inverter_communication", data)

    def update_communication(self, comm_id, data):
        return self.update_record("inverter_communication", comm_id, data)

    def delete_communication(self, comm_id):
        return self.delete_record("inverter_communication", comm_id)

    # --- Inverter Output Mode Operations ---
    def get_output_modes_for_inverter(self, inverter_id):
        query = "SELECT * FROM inverter_output_mode WHERE INVERTER_ID = ? ORDER BY ID"
        return self.fetch_all(query, (inverter_id,))

    def add_output_mode(self, data):
        return self.add_record("inverter_output_mode", data)

    def update_output_mode(self, mode_id, data):
        return self.update_record("inverter_output_mode", mode_id, data)

    def delete_output_mode(self, mode_id):
        return self.delete_record("inverter_output_mode", mode_id)

    # --- Module Operations ---
    def get_modules(self):
        query = """
            SELECT mod.*, m.NAME as MANUFACTURER_NAME 
            FROM module mod
            LEFT JOIN manufacturer m ON mod.MANUFACTURER_ID = m.ID
            ORDER BY mod.MODEL
        """
        return self.fetch_all(query)

    def add_module(self, data):
        return self.add_record("module", data)

    def update_module(self, module_id, data):
        return self.update_record("module", module_id, data)

    def delete_module(self, module_id):
        return self.delete_record("module", module_id)

# ==============================================================================
# Base Class for Frames (to reduce repetition)
# ==============================================================================
class BaseCrudFrame(ttk.Frame):
    """Classe base para frames de CRUD com Treeview e Formulário."""
    def __init__(self, parent, db_manager, table_name, fields_config, list_display_cols, 
                 form_title="Detalhes", list_title="Cadastrados", 
                 fk_configs=None, check_configs=None, numeric_fields=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.table_name = table_name
        self.fields_config = fields_config # Lista de nomes de campos do formulário
        self.list_display_cols = list_display_cols # Tupla de colunas para Treeview (nomes no DB)
        self.form_title = form_title
        self.list_title = list_title
        self.fk_configs = fk_configs or {} # {field_name: {fetch_func: db_manager.func, display_col: 'NAME', id_col: 'ID'}} 
        self.check_configs = check_configs or {} # {field_name: [val1, val2, ...]}
        self.numeric_fields = numeric_fields or {"int": [], "real": []} # {type: [field1, field2]}
        
        self.entries = {}
        self.selected_record_id = None
        self.foreign_key_data = {} # Cache para dados de FK {field_name: {display_val: id_val}}

        self._create_widgets()
        self._load_fk_data()
        self.load_records()

    def _create_widgets(self):
        # Frame Esquerdo: Lista (Treeview)
        list_frame = ttk.LabelFrame(self, text=self.list_title)
        list_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Configurar colunas da Treeview
        tree_cols = tuple(self.list_display_cols.keys()) # Usa as chaves do dict como identificadores
        self.tree = ttk.Treeview(list_frame, columns=tree_cols, show='headings', selectmode='browse')
        for col_id, col_config in self.list_display_cols.items():
            text = col_config.get('text', col_id.replace('_', ' ').title())
            width = col_config.get('width', 100)
            anchor = col_config.get('anchor', tk.W)
            self.tree.heading(col_id, text=text)
            self.tree.column(col_id, width=width, anchor=anchor)

        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_record_select)

        # Frame Direito: Formulário
        self.form_frame = ttk.LabelFrame(self, text=self.form_title)
        self.form_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        # Criar campos de entrada dinamicamente
        row_idx = 0
        for field in self.fields_config:
            if field == 'ID': continue # Não mostrar ID no formulário
            
            label_text = field.replace('_', ' ').title()
            label = ttk.Label(self.form_frame, text=f"{label_text}:")
            label.grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)

            if field in self.fk_configs:
                self.entries[field] = ttk.Combobox(self.form_frame, state='readonly', width=28)
                # Valores serão carregados em _load_fk_data
            elif field in self.check_configs:
                self.entries[field] = ttk.Combobox(self.form_frame, values=self.check_configs[field], state='readonly', width=28)
            else:
                self.entries[field] = ttk.Entry(self.form_frame, width=30)
            
            self.entries[field].grid(row=row_idx, column=1, sticky=tk.EW, padx=5, pady=2)
            row_idx += 1

        # Frame para botões
        button_frame = ttk.Frame(self.form_frame)
        button_frame.grid(row=row_idx, column=0, columnspan=2, pady=15)

        add_btn = ttk.Button(button_frame, text="Adicionar Novo", command=self.add_record)
        add_btn.pack(side=tk.LEFT, padx=5)
        update_btn = ttk.Button(button_frame, text="Atualizar", command=self.update_record)
        update_btn.pack(side=tk.LEFT, padx=5)
        delete_btn = ttk.Button(button_frame, text="Deletar", command=self.delete_record)
        delete_btn.pack(side=tk.LEFT, padx=5)
        clear_btn = ttk.Button(button_frame, text="Limpar", command=self.clear_fields)
        clear_btn.pack(side=tk.LEFT, padx=5)

    def _load_fk_data(self):
        """Carrega dados para os Comboboxes de chave estrangeira."""
        for field, config in self.fk_configs.items():
            fetch_func = config['fetch_func']
            display_col = config['display_col']
            id_col = config['id_col']
            
            try:
                fk_records = fetch_func() # Chama a função do db_manager
                self.foreign_key_data[field] = {str(rec[display_col]): rec[id_col] for rec in fk_records}
                self.entries[field]['values'] = list(self.foreign_key_data[field].keys())
            except Exception as e:
                messagebox.showerror("Erro FK", f"Erro ao carregar dados para {field}: {e}")
                self.entries[field]['values'] = []

    def load_records(self):
        """Carrega/Recarrega os registros na Treeview."""
        # Limpa a árvore
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Busca os dados (método a ser implementado/sobrescrito pela subclasse)
        records = self._fetch_records_for_list()
        
        # Preenche a árvore
        for record in records:
            values = []
            for col_id in self.list_display_cols.keys():
                # O valor pode vir diretamente do record ou de uma coluna renomeada (como MANUFACTURER_NAME)
                values.append(record.get(col_id, '')) 
            self.tree.insert('', tk.END, values=tuple(values))
        
        # Limpa a seleção e o formulário após recarregar
        self.clear_fields()
        # Emite evento para notificar outras partes (se necessário)
        self.event_generate(f"<<{self.table_name.capitalize()}ListUpdated>>")

    def _fetch_records_for_list(self):
        """Método para buscar os dados a serem exibidos na lista. Deve ser sobrescrito."""
        # Implementação padrão busca todos os registros da tabela
        # Pode não ser ideal se houver FKs que precisam de JOIN para exibição
        return self.db_manager.fetch_all(f"SELECT * FROM {self.table_name} ORDER BY ID")

    def on_record_select(self, event):
        """Chamado quando um registro é selecionado na Treeview."""
        selected_item = self.tree.focus()
        if not selected_item:
            self.selected_record_id = None
            self.clear_fields()
            return

        item_values = self.tree.item(selected_item, 'values')
        # Assumindo que a primeira coluna na Treeview é sempre o ID
        self.selected_record_id = item_values[0] 

        # Busca dados completos do registro selecionado
        record_data = self.db_manager.fetch_one(f"SELECT * FROM {self.table_name} WHERE ID = ?", (self.selected_record_id,))
        if not record_data:
            messagebox.showerror("Erro", f"Não foi possível carregar os dados do registro ID {self.selected_record_id}.")
            self.clear_fields()
            return

        # Preenche os campos do formulário
        for field in self.fields_config:
            if field == 'ID' or field not in self.entries: continue

            value = record_data.get(field)
            entry_widget = self.entries[field]

            # Limpa o campo antes de preencher
            if isinstance(entry_widget, ttk.Entry):
                entry_widget.delete(0, tk.END)
            elif isinstance(entry_widget, ttk.Combobox):
                entry_widget.set('')

            # Preenche com o valor
            if value is not None:
                if field in self.fk_configs:
                    # Encontra o valor de exibição correspondente ao ID armazenado
                    display_value = next((k for k, v in self.foreign_key_data[field].items() if v == value), "")
                    entry_widget.set(display_value)
                elif field in self.check_configs:
                    entry_widget.set(str(value)) # CHECK constraint values são strings ou números
                else:
                    entry_widget.insert(0, str(value))

    def get_field_data(self):
        """Coleta e valida os dados dos campos de entrada."""
        data = {}
        errors = []
        for field in self.fields_config:
            if field == 'ID' or field not in self.entries: continue

            entry_widget = self.entries[field]
            value_str = entry_widget.get()

            # Validações e Conversões
            is_required = self._is_field_required(field) # Checar se o campo é NOT NULL (simplificado)

            if not value_str and is_required:
                errors.append(f"{field.replace('_', ' ').title()} é obrigatório.")
                continue
            elif not value_str and not is_required:
                 data[field] = None # Permite nulo se não for obrigatório
                 continue

            # Conversões e validações específicas
            if field in self.fk_configs:
                fk_id = self.foreign_key_data[field].get(value_str)
                if fk_id is None:
                    errors.append(f"{field.replace('_', ' ').title()} inválido: {value_str}")
                else:
                    data[field] = fk_id
            elif field in self.check_configs:
                # A validação já é feita pelo Combobox, apenas pega o valor
                data[field] = value_str 
                # Converter para número se necessário (ex: ACTIVE=0/1)
                if all(v.isdigit() for v in self.check_configs[field]):
                    try:
                        data[field] = int(value_str)
                    except ValueError:
                         errors.append(f"{field.replace('_', ' ').title()} deve ser um número inteiro.")
            elif field in self.numeric_fields.get("int", []):
                try:
                    data[field] = int(value_str)
                except ValueError:
                    errors.append(f"{field.replace('_', ' ').title()} deve ser um número inteiro válido.")
            elif field in self.numeric_fields.get("real", []):
                 try:
                    data[field] = float(value_str)
                 except ValueError:
                    errors.append(f"{field.replace('_', ' ').title()} deve ser um número real válido.")
            else: # Campo de texto padrão
                data[field] = value_str

        if errors:
            messagebox.showerror("Erro de Validação", "\n".join(errors))
            return None
        return data

    def _is_field_required(self, field_name):
        """Verifica (de forma simplificada) se um campo é obrigatório.
           Idealmente, isso viria da introspecção do DB (NOT NULL).
           Aqui, vamos assumir alguns campos comuns como obrigatórios.
        """
        # Adicione aqui os campos que são NOT NULL na sua DB Schema
        required_fields_map = {
            "manufacturer": ["NAME"],
            "inverter": ["MODEL", "MANUFACTURER_ID", "COOLING_MODE", "PROTECTION_DEGREE", "TOPOLOGY", "ACTIVE"],
            "mppt": ["INVERTER_ID"], # MPPT_INDEX pode ter default 0
            "inverter_system": ["INVERTER_ID", "SYSTEM_TYPE"],
            "inverter_communication": ["INVERTER_ID", "COMMUNICATION_TYPE"],
            "inverter_output_mode": ["INVERTER_ID", "OUTPUT_MODE"],
            "module": ["MODEL", "MANUFACTURER_ID", "ACTIVE"]
        }
        return field_name in required_fields_map.get(self.table_name, [])

    def add_record(self):
        """Adiciona um novo registro."""
        data = self.get_field_data()
        if data:
            # Remover chaves com valor None para usar defaults do DB se necessário?
            # Ou manter None para inserir NULL explicitamente?
            # Vamos manter None por enquanto.
            # data_to_insert = {k: v for k, v in data.items() if v is not None}
            
            # Adicionar FKs que não estão no formulário (ex: INVERTER_ID em tabelas filhas)
            data = self._add_implicit_fks(data)
            if data is None: return # Erro ao obter FK implícita

            if self.db_manager.add_record(self.table_name, data):
                messagebox.showinfo("Sucesso", "Registro adicionado com sucesso!")
                self.load_records()
            # else: O db_manager já mostra o erro

    def update_record(self):
        """Atualiza o registro selecionado."""
        if not self.selected_record_id:
            messagebox.showwarning("Aviso", "Nenhum registro selecionado para atualizar.")
            return

        data = self.get_field_data()
        if data:
            # Remover chaves com valor None para atualização seletiva?
            # data_to_update = {k: v for k, v in data.items() if v is not None}
            
            # Adicionar FKs que não estão no formulário (se necessário para update? Geralmente não)
            # data = self._add_implicit_fks(data) 
            # if data is None: return

            if self.db_manager.update_record(self.table_name, self.selected_record_id, data):
                messagebox.showinfo("Sucesso", "Registro atualizado com sucesso!")
                self.load_records()
            # else: O db_manager já mostra o erro

    def delete_record(self):
        """Deleta o registro selecionado."""
        if not self.selected_record_id:
            messagebox.showwarning("Aviso", "Nenhum registro selecionado para deletar.")
            return

        # Adicionar confirmação específica se houver filhos com ON DELETE CASCADE
        confirm_msg = f"Tem certeza que deseja deletar o registro ID {self.selected_record_id}?"
        if self.table_name == 'inverter':
             confirm_msg += "\nTodos os MPPTs, Sistemas, Comunicações e Modos de Saída associados também serão removidos."
        elif self.table_name == 'manufacturer':
             confirm_msg += "\nA exclusão pode falhar se houver Inversores ou Módulos associados."

        if messagebox.askyesno("Confirmar Exclusão", confirm_msg):
            if self.db_manager.delete_record(self.table_name, self.selected_record_id):
                messagebox.showinfo("Sucesso", "Registro deletado com sucesso!")
                self.load_records()
            # else: O db_manager já mostra o erro

    def clear_fields(self):
        """Limpa todos os campos de entrada e a seleção."""
        self.selected_record_id = None
        current_focus = self.tree.focus()
        if current_focus:
            self.tree.selection_remove(current_focus)
            
        for field in self.fields_config:
             if field == 'ID' or field not in self.entries: continue
             entry = self.entries[field]
             if isinstance(entry, ttk.Entry):
                 entry.delete(0, tk.END)
             elif isinstance(entry, ttk.Combobox):
                 entry.set('')
                 
    def _add_implicit_fks(self, data):
         """Adiciona chaves estrangeiras que não estão no formulário, 
            mas são necessárias (ex: INVERTER_ID em tabelas filhas).
            Deve ser sobrescrito nas classes filhas que precisam disso.
         """
         return data # Implementação padrão não faz nada

# ==============================================================================
# Frame Classes Específicas
# ==============================================================================

# --- Manufacturer Frame ---
class ManufacturerFrame(BaseCrudFrame):
    def __init__(self, parent, db_manager):
        fields = ['NAME', 'CATEGORY']
        list_cols = {
            'ID': {'text': 'ID', 'width': 50, 'anchor': tk.CENTER},
            'NAME': {'text': 'Nome', 'width': 200},
            'CATEGORY': {'text': 'Categoria', 'width': 80, 'anchor': tk.CENTER}
        }
        check_cfg = {'CATEGORY': ['0', '1', '2']}
        num_fields = {"int": ["CATEGORY"]}
        
        super().__init__(parent, db_manager, 'manufacturer', fields, list_cols, 
                         form_title="Detalhes do Fabricante", 
                         list_title="Fabricantes Cadastrados",
                         check_configs=check_cfg,
                         numeric_fields=num_fields)

    def _fetch_records_for_list(self):
        return self.db_manager.get_manufacturers()

# --- Inverter Frame ---
class InverterFrame(BaseCrudFrame):
    def __init__(self, parent, db_manager):
        fields = [
            'MODEL', 'MANUFACTURER_ID', 'DIM_WIDTH', 'DIM_HEIGHT', 'DIM_DEPTH', 'DIM_WEIGHT',
            'MAX_OPERATING_TEMPERATURE', 'MIN_OPERATING_TEMPERATURE', 'COOLING_MODE',
            'PROTECTION_DEGREE', 'TOPOLOGY', 'RATED_ACTIVE_POWER', 'MAX_ACTIVE_POWER',
            'RATED_OUTPUT_VOLTAGE', 'RATED_OUTPUT_CURRENT', 'MAX_OUTPUT_CURRENT', 'OVERLOAD',
            'NUMBER_OF_TRACKERS', 'NUMBER_OF_INPUTS', 'ACTIVE'
        ]
        list_cols = {
            'ID': {'text': 'ID', 'width': 40, 'anchor': tk.CENTER},
            'MODEL': {'text': 'Modelo', 'width': 150},
            'MANUFACTURER_NAME': {'text': 'Fabricante', 'width': 150}, # Vem do JOIN
            'ACTIVE': {'text': 'Ativo', 'width': 50, 'anchor': tk.CENTER}
        }
        fk_cfg = {
            'MANUFACTURER_ID': {
                'fetch_func': db_manager.get_manufacturers, 
                'display_col': 'NAME', 
                'id_col': 'ID'
            }
        }
        check_cfg = {'ACTIVE': ['0', '1']}
        num_fields = {
            "int": ['MAX_OPERATING_TEMPERATURE', 'MIN_OPERATING_TEMPERATURE', 
                    'RATED_ACTIVE_POWER', 'MAX_ACTIVE_POWER', 'OVERLOAD', 
                    'NUMBER_OF_TRACKERS', 'NUMBER_OF_INPUTS', 'ACTIVE'],
            "real": ['DIM_WIDTH', 'DIM_HEIGHT', 'DIM_DEPTH', 'DIM_WEIGHT',
                     'RATED_OUTPUT_VOLTAGE', 'RATED_OUTPUT_CURRENT', 'MAX_OUTPUT_CURRENT']
        }

        super().__init__(parent, db_manager, 'inverter', fields, list_cols, 
                         form_title="Detalhes do Inversor", 
                         list_title="Inversores Cadastrados",
                         fk_configs=fk_cfg,
                         check_configs=check_cfg,
                         numeric_fields=num_fields)

    def _fetch_records_for_list(self):
        # Usa a função específica que faz o JOIN com manufacturer
        return self.db_manager.get_inverters()

    def load_records(self):
        # Sobrescreve para também recarregar fabricantes caso a lista mude
        self._load_fk_data() 
        super().load_records()

# --- Base Frame for Inverter Child Tables (MPPT, System, Comm, Output) ---
class BaseInverterChildFrame(BaseCrudFrame):
    def __init__(self, parent, db_manager, table_name, fields_config, list_display_cols, 
                 form_title, list_title_base, 
                 check_configs=None, numeric_fields=None):
        
        self.inverters = {} # Cache para {display_name: id}
        self.selected_inverter_id = None
        self.list_title_base = list_title_base

        # Não incluir INVERTER_ID nos fields_config normais, será tratado separadamente
        actual_fields_config = [f for f in fields_config if f != 'INVERTER_ID']

        super().__init__(parent, db_manager, table_name, actual_fields_config, list_display_cols, 
                         form_title=form_title, 
                         list_title=f"{list_title_base} (Selecione um Inversor)", # Título inicial
                         check_configs=check_configs,
                         numeric_fields=numeric_fields)
        
        # Remover o frame de lista padrão e recriar com combobox de inversor acima
        self.children['!labelframe'].destroy() # Destroi o list_frame criado pelo pai
        self.children['!labelframe2'].destroy() # Destroi o form_frame criado pelo pai

        # Frame Superior: Seleção de Inversor
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10,0))
        inverter_select_label = ttk.Label(top_frame, text="Selecionar Inversor:")
        inverter_select_label.pack(side=tk.LEFT, padx=(0, 5))
        self.inverter_combobox = ttk.Combobox(top_frame, state='readonly', width=40)
        self.inverter_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.inverter_combobox.bind('<<ComboboxSelected>>', self.on_inverter_selected)

        # Frame Esquerdo: Lista (Treeview) - Recriado
        self.list_frame = ttk.LabelFrame(self, text=self.list_title) # Usa o título atualizado
        self.list_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        # Recria a Treeview e scrollbars dentro do novo list_frame
        self._recreate_treeview(self.list_frame)

        # Frame Direito: Formulário - Recriado
        self.form_frame = ttk.LabelFrame(self, text=self.form_title)
        self.form_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)
        # Recria os campos e botões dentro do novo form_frame
        self._recreate_form_fields(self.form_frame)

        # Carrega a lista inicial de inversores
        self.update_inverter_list()

    def _recreate_treeview(self, parent_frame):
        tree_cols = tuple(self.list_display_cols.keys())
        self.tree = ttk.Treeview(parent_frame, columns=tree_cols, show='headings', selectmode='browse')
        for col_id, col_config in self.list_display_cols.items():
            text = col_config.get('text', col_id.replace('_', ' ').title())
            width = col_config.get('width', 100)
            anchor = col_config.get('anchor', tk.W)
            self.tree.heading(col_id, text=text)
            self.tree.column(col_id, width=width, anchor=anchor)
        vsb = ttk.Scrollbar(parent_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(parent_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_record_select)

    def _recreate_form_fields(self, parent_frame):
        self.entries = {} # Reinicia o dict de entries
        row_idx = 0
        for field in self.fields_config: # Usa a lista original sem ID
            if field == 'ID': continue
            label_text = field.replace('_', ' ').title()
            label = ttk.Label(parent_frame, text=f"{label_text}:")
            label.grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)
            if field in self.check_configs:
                self.entries[field] = ttk.Combobox(parent_frame, values=self.check_configs[field], state='readonly', width=28)
            else:
                self.entries[field] = ttk.Entry(parent_frame, width=30)
            self.entries[field].grid(row=row_idx, column=1, sticky=tk.EW, padx=5, pady=2)
            row_idx += 1
        # Botões
        button_frame = ttk.Frame(parent_frame)
        button_frame.grid(row=row_idx, column=0, columnspan=2, pady=15)
        add_btn = ttk.Button(button_frame, text="Adicionar Novo", command=self.add_record)
        add_btn.pack(side=tk.LEFT, padx=5)
        update_btn = ttk.Button(button_frame, text="Atualizar", command=self.update_record)
        update_btn.pack(side=tk.LEFT, padx=5)
        delete_btn = ttk.Button(button_frame, text="Deletar", command=self.delete_record)
        delete_btn.pack(side=tk.LEFT, padx=5)
        clear_btn = ttk.Button(button_frame, text="Limpar", command=self.clear_fields)
        clear_btn.pack(side=tk.LEFT, padx=5)

    def update_inverter_list(self, event=None):
        """Atualiza a lista de inversores no Combobox."""
        inverters_data = self.db_manager.get_inverters()
        self.inverters = {f"{inv['MODEL']} (ID: {inv['ID']})": inv['ID'] for inv in inverters_data}
        self.inverter_combobox['values'] = list(self.inverters.keys())
        
        current_selection_text = self.inverter_combobox.get()
        if current_selection_text not in self.inverters:
            self.inverter_combobox.set('')
            self.selected_inverter_id = None
            self.list_frame.config(text=f"{self.list_title_base} (Selecione um Inversor)")
            self.load_records() # Limpa a lista de filhos
        else:
            # Mantém a seleção e força recarga dos filhos
            self.on_inverter_selected()

    def on_inverter_selected(self, event=None):
        """Chamado quando um inversor é selecionado no Combobox."""
        selected_text = self.inverter_combobox.get()
        new_inverter_id = self.inverters.get(selected_text)
        if new_inverter_id != self.selected_inverter_id:
            self.selected_inverter_id = new_inverter_id
            if self.selected_inverter_id:
                 self.list_frame.config(text=f"{self.list_title_base} (Inversor ID: {self.selected_inverter_id})")
            else:
                 self.list_frame.config(text=f"{self.list_title_base} (Selecione um Inversor)")
            self.load_records()

    def load_records(self):
        """Carrega/Recarrega os registros na Treeview para o inversor selecionado."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        records = []
        if self.selected_inverter_id:
            records = self._fetch_records_for_list() # Chama o método da subclasse
        
        for record in records:
            values = [record.get(col_id, '') for col_id in self.list_display_cols.keys()]
            self.tree.insert('', tk.END, values=tuple(values))
        
        self.clear_fields()

    def _add_implicit_fks(self, data):
        """Adiciona INVERTER_ID aos dados antes de inserir."""
        if not self.selected_inverter_id:
             messagebox.showwarning("Aviso", "Selecione um inversor antes de adicionar.")
             return None
        data['INVERTER_ID'] = self.selected_inverter_id
        return data

    def add_record(self):
        """Verifica se um inversor está selecionado antes de adicionar."""
        if not self.selected_inverter_id:
            messagebox.showwarning("Aviso", "Selecione um inversor primeiro.")
            return
        super().add_record()

# --- MPPT Frame ---
class MpptFrame(BaseInverterChildFrame):
    def __init__(self, parent, db_manager):
        fields = [
            'INVERTER_ID', # Necessário para a lógica interna, mas não no form principal
            'MPPT_INDEX', 'NUMBER_OF_INPUTS', 'MAX_INPUT_VOLTAGE', 'MIN_STARTUP_VOLTAGE',
            'MAX_OPERATING_VOLTAGE', 'MIN_OPERATING_VOLTAGE', 'MAX_FULL_LOAD_VOLTAGE',
            'MIN_FULL_LOAD_VOLTAGE', 'RATED_INPUT_VOLTAGE', 'MAX_SHORT_CIRCUIT_CURRENT',
            'MAX_OPERATING_CURRENT'
        ]
        list_cols = {
            'ID': {'text': 'ID', 'width': 40, 'anchor': tk.CENTER},
            'MPPT_INDEX': {'text': 'Índice', 'width': 50, 'anchor': tk.CENTER},
            'NUMBER_OF_INPUTS': {'text': 'Nº Entradas', 'width': 80},
            'MAX_INPUT_VOLTAGE': {'text': 'Max V Entrada', 'width': 100},
            'MIN_STARTUP_VOLTAGE': {'text': 'Min V Partida', 'width': 100},
            'MAX_OPERATING_VOLTAGE': {'text': 'Max V Oper.', 'width': 100},
            'MIN_OPERATING_VOLTAGE': {'text': 'Min V Oper.', 'width': 100},
            'MAX_OPERATING_CURRENT': {'text': 'Max I Oper.', 'width': 100},
            'MAX_SHORT_CIRCUIT_CURRENT': {'text': 'Max Isc', 'width': 100},
        }
        num_fields = {
            "int": ['MPPT_INDEX', 'NUMBER_OF_INPUTS', 'MAX_INPUT_VOLTAGE', 
                    'MIN_STARTUP_VOLTAGE', 'MAX_OPERATING_VOLTAGE', 
                    'MIN_OPERATING_VOLTAGE', 'MAX_FULL_LOAD_VOLTAGE', 
                    'MIN_FULL_LOAD_VOLTAGE', 'RATED_INPUT_VOLTAGE'],
            "real": ['MAX_SHORT_CIRCUIT_CURRENT', 'MAX_OPERATING_CURRENT']
        }
        super().__init__(parent, db_manager, 'mppt', fields, list_cols, 
                         form_title="Detalhes do MPPT", 
                         list_title_base="MPPTs",
                         numeric_fields=num_fields)

    def _fetch_records_for_list(self):
        if self.selected_inverter_id:
            return self.db_manager.get_mppts_for_inverter(self.selected_inverter_id)
        return []

# --- Inverter System Frame ---
class InverterSystemFrame(BaseInverterChildFrame):
     def __init__(self, parent, db_manager):
        fields = ['INVERTER_ID', 'SYSTEM_TYPE']
        list_cols = {
            'ID': {'text': 'ID', 'width': 50, 'anchor': tk.CENTER},
            'SYSTEM_TYPE': {'text': 'Tipo de Sistema', 'width': 200}
        }
        check_cfg = {'SYSTEM_TYPE': ['ON-GRID', 'OFF-GRID', 'GRIDZERO', 'HYBRID']}
        
        super().__init__(parent, db_manager, 'inverter_system', fields, list_cols, 
                         form_title="Tipo de Sistema do Inversor", 
                         list_title_base="Sistemas",
                         check_configs=check_cfg)

     def _fetch_records_for_list(self):
        if self.selected_inverter_id:
            return self.db_manager.get_systems_for_inverter(self.selected_inverter_id)
        return []

# --- Inverter Communication Frame ---
class InverterCommunicationFrame(BaseInverterChildFrame):
     def __init__(self, parent, db_manager):
        fields = ['INVERTER_ID', 'COMMUNICATION_TYPE']
        list_cols = {
            'ID': {'text': 'ID', 'width': 50, 'anchor': tk.CENTER},
            'COMMUNICATION_TYPE': {'text': 'Tipo de Comunicação', 'width': 200}
        }
        check_cfg = {'COMMUNICATION_TYPE': ['DISPLAY', 'RS485', 'WIFI', 'LED', 'USB', '4G']}
        
        super().__init__(parent, db_manager, 'inverter_communication', fields, list_cols, 
                         form_title="Comunicação do Inversor", 
                         list_title_base="Comunicações",
                         check_configs=check_cfg)

     def _fetch_records_for_list(self):
        if self.selected_inverter_id:
            return self.db_manager.get_communications_for_inverter(self.selected_inverter_id)
        return []

# --- Inverter Output Mode Frame ---
class InverterOutputModeFrame(BaseInverterChildFrame):
     def __init__(self, parent, db_manager):
        fields = ['INVERTER_ID', 'OUTPUT_MODE']
        list_cols = {
            'ID': {'text': 'ID', 'width': 50, 'anchor': tk.CENTER},
            'OUTPUT_MODE': {'text': 'Modo de Saída', 'width': 200}
        }
        check_cfg = {'OUTPUT_MODE': ['THREE_PHASE_FOUR_WIRE', 'THREE_PHASE_THREE_WIRE', 'SINGLE_PHASE']}
        
        super().__init__(parent, db_manager, 'inverter_output_mode', fields, list_cols, 
                         form_title="Modo de Saída do Inversor", 
                         list_title_base="Modos de Saída",
                         check_configs=check_cfg)

     def _fetch_records_for_list(self):
        if self.selected_inverter_id:
            return self.db_manager.get_output_modes_for_inverter(self.selected_inverter_id)
        return []

# --- Module Frame ---
class ModuleFrame(BaseCrudFrame):
    def __init__(self, parent, db_manager):
        fields = [
            'MODEL', 'MANUFACTURER_ID', 'DIM_WIDTH', 'DIM_HEIGHT', 'DIM_DEPTH', 'DIM_WEIGHT',
            'WP', 'VMPP', 'IMPP', 'VOC', 'ISC',
            'SOLAR_CELLS', 'CELL_TYPE', 'SURFACE_TYPE',
            'COEF_PMAX', 'COEF_VOC', 'COEF_ISC', 'ACTIVE'
        ]
        list_cols = {
            'ID': {'text': 'ID', 'width': 40, 'anchor': tk.CENTER},
            'MODEL': {'text': 'Modelo', 'width': 150},
            'MANUFACTURER_NAME': {'text': 'Fabricante', 'width': 150}, # Vem do JOIN
            'WP': {'text': 'Potência (Wp)', 'width': 80},
            'ACTIVE': {'text': 'Ativo', 'width': 50, 'anchor': tk.CENTER}
        }
        fk_cfg = {
            'MANUFACTURER_ID': {
                'fetch_func': db_manager.get_manufacturers, 
                'display_col': 'NAME', 
                'id_col': 'ID'
            }
        }
        check_cfg = {
            'SOLAR_CELLS': ['MONOCRISTALINO', 'POLICRISTALINO'],
            'CELL_TYPE': ['FULL CELL', 'HALF CELL'],
            'SURFACE_TYPE': ['MONOFACIAL', 'BIFACIAL'],
            'ACTIVE': ['0', '1']
        }
        num_fields = {
            "int": ['WP', 'ACTIVE'],
            "real": ['DIM_WIDTH', 'DIM_HEIGHT', 'DIM_DEPTH', 'DIM_WEIGHT',
                     'VMPP', 'IMPP', 'VOC', 'ISC',
                     'COEF_PMAX', 'COEF_VOC', 'COEF_ISC']
        }

        super().__init__(parent, db_manager, 'module', fields, list_cols, 
                         form_title="Detalhes do Módulo", 
                         list_title="Módulos Cadastrados",
                         fk_configs=fk_cfg,
                         check_configs=check_cfg,
                         numeric_fields=num_fields)

    def _fetch_records_for_list(self):
        # Usa a função específica que faz o JOIN com manufacturer
        return self.db_manager.get_modules()

    def load_records(self):
        # Sobrescreve para também recarregar fabricantes caso a lista mude
        self._load_fk_data()
        super().load_records()

# ==============================================================================
# Main Application Class
# ==============================================================================
class App(tk.Tk):
    """Aplicação principal Tkinter."""
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.title("Gerenciador Completo Optimus Sun DB")
        # Aumentar tamanho da janela para acomodar mais abas e campos

        w_scr = self.winfo_screenwidth()
        h_scr = self.winfo_screenheight()
        self.geometry(f"{w_scr}x{h_scr}+0+0") 

        # Estilo
        style = ttk.Style(self)
        style.theme_use('clam') # Ou outro tema: alt, default, classic

        # Notebook para abas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill='both')

        # --- Criar Instâncias das Abas ---
        self.manufacturer_frame = ManufacturerFrame(self.notebook, self.db_manager)
        self.inverter_frame = InverterFrame(self.notebook, self.db_manager)
        self.module_frame = ModuleFrame(self.notebook, self.db_manager)
        self.mppt_frame = MpptFrame(self.notebook, self.db_manager)
        self.system_frame = InverterSystemFrame(self.notebook, self.db_manager)
        self.comm_frame = InverterCommunicationFrame(self.notebook, self.db_manager)
        self.output_mode_frame = InverterOutputModeFrame(self.notebook, self.db_manager)

        # --- Adicionar Abas ao Notebook ---
        self.notebook.add(self.manufacturer_frame, text='Fabricantes')
        self.notebook.add(self.inverter_frame, text='Inversores')
        self.notebook.add(self.module_frame, text='Módulos')
        self.notebook.add(self.mppt_frame, text='MPPTs')
        self.notebook.add(self.system_frame, text='Sistemas Inversor')
        self.notebook.add(self.comm_frame, text='Comunicação Inversor')
        self.notebook.add(self.output_mode_frame, text='Modo Saída Inversor')

        # --- Configurar Eventos de Atualização entre Abas ---
        # Quando Fabricantes mudam, atualizar combos em Inversores e Módulos
        self.manufacturer_frame.bind("<<ManufacturerListUpdated>>", self.inverter_frame.load_records)
        self.manufacturer_frame.bind("<<ManufacturerListUpdated>>", self.module_frame.load_records)
        
        # Quando Inversores mudam, atualizar combos em MPPTs, Sistemas, Comunicação, Modo Saída
        self.inverter_frame.bind("<<InverterListUpdated>>", self.mppt_frame.update_inverter_list)
        self.inverter_frame.bind("<<InverterListUpdated>>", self.system_frame.update_inverter_list)
        self.inverter_frame.bind("<<InverterListUpdated>>", self.comm_frame.update_inverter_list)
        self.inverter_frame.bind("<<InverterListUpdated>>", self.output_mode_frame.update_inverter_list)

# ==============================================================================
# Entry Point
# ==============================================================================
if __name__ == "__main__":
    # Verifica se o banco de dados existe antes de iniciar
    if not os.path.exists(DATABASE_NAME):
        # Tenta criar as tabelas se o DB não existir
        try:
            # Assume que optimus_sun_db.py está no mesmo diretório
            import optimus_sun_db 
            optimus_sun_db.criar_tabela()
            print(f"Banco de dados '{DATABASE_NAME}' e tabelas criados.")
        except ImportError:
             messagebox.showerror("Erro Crítico", f"Arquivo 'optimus_sun_db.py' não encontrado para criar o banco de dados inicial.")
             exit()
        except Exception as e:
             messagebox.showerror("Erro Crítico", f"Falha ao criar tabelas no banco de dados: {e}")
             exit()

    try:
        db_manager = DatabaseManager(DATABASE_NAME)
        app = App(db_manager)
        app.mainloop()
    except FileNotFoundError:
        # O erro já foi mostrado pelo DatabaseManager
        pass 
    except Exception as e:
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado na aplicação: {e}")
