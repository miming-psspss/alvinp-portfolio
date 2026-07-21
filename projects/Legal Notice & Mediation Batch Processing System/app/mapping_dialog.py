"""
Import mapping dialog: lets the user pick a sheet, confirm/adjust the header
row, and map each of their spreadsheet's columns to a system field before
anything gets imported. This is what makes the program adapt to whatever
Excel file the user brings, instead of requiring one fixed layout.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox, QLabel,
    QPushButton, QSpinBox, QScrollArea, QWidget, QMessageBox, QDialogButtonBox
)

from app.schema_fields import SCHEMA_FIELDS, REQUIRED_FIELDS
from app.import_mapping import (
    list_sheets, read_headers, guess_mapping, load_saved_mapping, save_mapping
)


class ImportMappingDialog(QDialog):
    def __init__(self, filepath: str, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self.setWindowTitle("Map Your Columns")
        self.resize(600, 650)
        self.field_combos = {}  # field_key -> QComboBox

        outer = QVBoxLayout(self)

        outer.addWidget(QLabel(
            "Match each field the program needs to a column from your file.\n"
            "Fields with no matching column can be left as \"-- Skip --\"."
        ))

        # --- Sheet + header row selection ---
        top_form = QFormLayout()
        self.sheet_combo = QComboBox()
        self.sheet_combo.addItems(list_sheets(filepath))
        self.sheet_combo.currentTextChanged.connect(self.on_sheet_changed)
        top_form.addRow("Sheet:", self.sheet_combo)

        self.header_row_spin = QSpinBox()
        self.header_row_spin.setMinimum(1)
        self.header_row_spin.setMaximum(100)
        self.header_row_spin.valueChanged.connect(self.on_header_row_changed)
        top_form.addRow("Header row number:", self.header_row_spin)
        outer.addLayout(top_form)

        self.header_preview_label = QLabel("")
        self.header_preview_label.setWordWrap(True)
        self.header_preview_label.setStyleSheet("color: #555; font-style: italic;")
        outer.addWidget(self.header_preview_label)

        suggest_row = QHBoxLayout()
        suggest_btn = QPushButton("Re-suggest Mapping")
        suggest_btn.clicked.connect(self.apply_suggestions)
        suggest_row.addWidget(suggest_btn)
        suggest_row.addStretch()
        outer.addLayout(suggest_row)

        # --- Scrollable field mapping form ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        mapping_widget = QWidget()
        self.mapping_form = QFormLayout(mapping_widget)
        for field_key, (label, required, _aliases) in SCHEMA_FIELDS.items():
            combo = QComboBox()
            display_label = f"{label} *" if required else label
            self.field_combos[field_key] = combo
            self.mapping_form.addRow(display_label, combo)
        scroll.setWidget(mapping_widget)
        outer.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.on_accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)

        self.result_mapping = None
        self.result_sheet = None
        self.result_header_row = None

        # Initialize with the first sheet
        self.on_sheet_changed(self.sheet_combo.currentText())

    def _current_headers(self):
        return read_headers(self.filepath, self.sheet_combo.currentText(), self.header_row_spin.value())

    def on_sheet_changed(self, sheet_name):
        if not sheet_name:
            return
        # Best-guess header row: look for the row with the most text cells in the first 20 rows
        self.header_row_spin.blockSignals(True)
        self.header_row_spin.setValue(self._guess_header_row(sheet_name))
        self.header_row_spin.blockSignals(False)
        self.refresh_headers_and_mapping()

    def _guess_header_row(self, sheet_name, max_scan=20):
        best_row, best_count = 1, 0
        for row_num in range(1, max_scan + 1):
            headers = read_headers(self.filepath, sheet_name, row_num)
            non_empty = sum(1 for h in headers if h)
            if non_empty > best_count:
                best_count, best_row = non_empty, row_num
        return best_row

    def on_header_row_changed(self, _value):
        self.refresh_headers_and_mapping()

    def refresh_headers_and_mapping(self):
        headers = self._current_headers()
        preview = ", ".join(h for h in headers if h)[:200]
        self.header_preview_label.setText(f"Detected columns: {preview}" if preview else "No headers detected on this row.")

        for combo in self.field_combos.values():
            combo.clear()
            combo.addItem("-- Skip --", None)
            for i, h in enumerate(headers):
                if h:
                    combo.addItem(h, i)

        # Try a remembered mapping for this exact header set first; fall back to auto-guess
        remembered = load_saved_mapping(headers)  # {col_index: field_key}
        if remembered:
            field_to_col = {field: col for col, field in remembered.items() if field}
            self._apply_mapping_to_combos(field_to_col)
        else:
            self.apply_suggestions()

    def apply_suggestions(self):
        headers = self._current_headers()
        suggested = guess_mapping(headers)  # {col_index: field_key or None}
        field_to_col = {field: col for col, field in suggested.items() if field}
        self._apply_mapping_to_combos(field_to_col)

    def _apply_mapping_to_combos(self, field_to_col: dict):
        for field_key, combo in self.field_combos.items():
            col = field_to_col.get(field_key)
            target_index = 0  # "-- Skip --"
            if col is not None:
                idx = combo.findData(col)
                if idx >= 0:
                    target_index = idx
            combo.setCurrentIndex(target_index)

    def on_accept(self):
        mapping = {}
        for field_key, combo in self.field_combos.items():
            col = combo.currentData()
            if col is not None:
                mapping[col] = field_key

        mapped_fields = set(mapping.values())
        missing_required = [f for f in REQUIRED_FIELDS if f not in mapped_fields]
        if missing_required:
            labels = [SCHEMA_FIELDS[f][0] for f in missing_required]
            QMessageBox.warning(
                self, "Missing required fields",
                f"Please map a column for: {', '.join(labels)}"
            )
            return

        self.result_mapping = mapping
        self.result_sheet = self.sheet_combo.currentText()
        self.result_header_row = self.header_row_spin.value()
        save_mapping(self._current_headers(), mapping)
        self.accept()
