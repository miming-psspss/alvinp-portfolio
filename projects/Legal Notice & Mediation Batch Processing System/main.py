"""
Legal Notice & Mediation Batch Processing System - v1 (GUI)

Narrow v1 scope: Statement of Account only, end-to-end.
Other document types (Mediation Forms 2-10, Envelope, etc.) plug into the
same field-map + template pattern -- they're just not wired up yet.
"""
import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QComboBox, QMessageBox, QHeaderView, QAbstractItemView, QGroupBox,
    QTextEdit, QFileDialog
)
from PySide6.QtCore import Qt

from app.db import init_db, list_cases, get_case, log_generation, get_generation_history
from app.generator import generate_document, ValidationError, FIELD_MAPS_DIR
from app.import_mapping import import_with_mapping
from app.mapping_dialog import ImportMappingDialog

AVAILABLE_DOCUMENT_TYPES = {
    "statement_of_account": "Statement of Account",
    "mediation_statement_options": "Mediation Statement Options",
    "mediation_form2": "Mediation Form 2 - Formal Charge",
    "mediation_form3": "Mediation Form 3 - Notice",
    "mediation_form3a": "Mediation Form 3.a - 2nd and Final Notice",
    "envelope": "Envelope",
    "mediation_form4": "Mediation Form 4 - Tracking Form",
    "mediation_form5": "Mediation Form 5 - Agreement to Mediate",
    "mediation_form6": "Mediation Form 6 - Settlement Agreement",
    "mediation_form8": "Mediation Form 8 - Evaluation",
    "mediation_form9": "Mediation Form 9 - Mediator's Report",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Legal Notice & Mediation Batch Processing System")
        self.resize(900, 600)
        self.selected_case_no = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # --- Import bar ---
        import_row = QHBoxLayout()
        self.import_btn = QPushButton("Import Cases from Excel...")
        self.import_btn.clicked.connect(self.on_import_clicked)
        import_row.addWidget(self.import_btn)
        self.data_status_label = QLabel("")
        import_row.addWidget(self.data_status_label)
        import_row.addStretch()
        layout.addLayout(import_row)

        # --- Search bar ---
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search member name:"))
        self.search_box = QLineEdit()
        self.search_box.textChanged.connect(self.refresh_case_list)
        search_row.addWidget(self.search_box)
        layout.addLayout(search_row)

        # --- Case table ---
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Case No.", "Member", "Loan Type", "Total Due"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_case_selected)
        layout.addWidget(self.table)

        # --- Generation panel ---
        gen_box = QGroupBox("Generate document")
        gen_layout = QHBoxLayout(gen_box)
        gen_layout.addWidget(QLabel("Document type:"))
        self.doc_type_combo = QComboBox()
        for key, label in AVAILABLE_DOCUMENT_TYPES.items():
            self.doc_type_combo.addItem(label, key)
        gen_layout.addWidget(self.doc_type_combo)
        self.generate_btn = QPushButton("Generate")
        self.generate_btn.clicked.connect(self.on_generate_clicked)
        self.generate_btn.setEnabled(False)
        gen_layout.addWidget(self.generate_btn)
        layout.addWidget(gen_box)

        # --- History panel ---
        history_box = QGroupBox("Generation history for selected case")
        history_layout = QVBoxLayout(history_box)
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setMaximumHeight(120)
        history_layout.addWidget(self.history_text)
        layout.addWidget(history_box)

        self.status_label = QLabel("Ready.")
        layout.addWidget(self.status_label)

        self.refresh_case_list()

    def on_import_clicked(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select case data file", "", "Excel Files (*.xlsx *.xlsm);;All Files (*)"
        )
        if not path:
            return

        dialog = ImportMappingDialog(path, self)
        if dialog.exec() != ImportMappingDialog.Accepted:
            return

        try:
            count = import_with_mapping(
                path, dialog.result_sheet, dialog.result_header_row, dialog.result_mapping
            )
        except ValueError as e:
            QMessageBox.critical(self, "Import failed", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Import failed", f"Unexpected error reading this file:\n{e}")
            return

        self.data_status_label.setText(f"Loaded {count} cases from {Path(path).name}")
        self.status_label.setText(f"Imported {count} cases.")
        self.refresh_case_list()
        QMessageBox.information(self, "Import complete", f"Loaded {count} cases from:\n{path}")

    def refresh_case_list(self):
        cases = list_cases(self.search_box.text())
        self.table.setRowCount(0)
        for row_idx, case in enumerate(cases):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(case["case_no"])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(case["member_name"]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(case["kind_of_loan"] or ""))
            total = case["total_amount_due"]
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{total:,.2f}" if total else ""))

        if not cases and not self.search_box.text():
            self.status_label.setText(
                "No cases loaded yet. Click \"Import Cases from Excel...\" above to get started."
            )

    def on_case_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            self.selected_case_no = None
            self.generate_btn.setEnabled(False)
            self.history_text.clear()
            return
        row = selected[0].row()
        self.selected_case_no = int(self.table.item(row, 0).text())
        self.generate_btn.setEnabled(True)
        self.refresh_history()

    def refresh_history(self):
        history = get_generation_history(self.selected_case_no)
        if not history:
            self.history_text.setPlainText("No documents generated yet for this case.")
            return
        lines = [f"{h['generated_at']}  --  {h['document_type']}  --  {h['output_path']}" for h in history]
        self.history_text.setPlainText("\n".join(lines))

    def on_generate_clicked(self):
        if self.selected_case_no is None:
            return
        doc_type_key = self.doc_type_combo.currentData()
        case = get_case(self.selected_case_no)

        try:
            output_path = generate_document(case, doc_type_key)
        except ValidationError as e:
            QMessageBox.warning(self, "Cannot generate document", str(e))
            self.status_label.setText(f"Blocked: {e}")
            return
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Document type not available", str(e))
            return

        log_generation(
            self.selected_case_no,
            AVAILABLE_DOCUMENT_TYPES[doc_type_key],
            str(output_path),
            datetime.now().isoformat(timespec="seconds"),
        )
        self.status_label.setText(f"Generated: {output_path.name}")
        self.refresh_history()
        QMessageBox.information(self, "Document generated", f"Saved to:\n{output_path}")


def main():
    init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
