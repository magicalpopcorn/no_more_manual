from PyQt6.QtWidgets import QLabel, QPushButton, QTableView, QVBoxLayout, QWidget

from ..data_obj import DataFrameModel


class ResourceTab(QWidget):
    def __init__(self):

        super().__init__()
        resource_layout = QVBoxLayout()

        # Example content for the Report tab
        self.avail_table = QTableView()
        self.total_table = QTableView()

        # Table view for showing DataFrames
        resource_layout.addWidget(QLabel("Available Resources"))
        resource_layout.addWidget(self.avail_table)
        resource_layout.addWidget(QLabel("Total Resources"))
        resource_layout.addWidget(self.total_table)

        generate_btn = QPushButton("Generate Report")
        generate_btn.clicked.connect(self.load_report)
        resource_layout.addWidget(generate_btn)

        self.setLayout(resource_layout)

    def load_report(self):
        from tools import report

        avail_df, total_df = report.process_rss()

        self.avail_table.setModel(DataFrameModel(avail_df))
        self.avail_table.resizeColumnsToContents()

        self.total_table.setModel(DataFrameModel(total_df))
        self.total_table.resizeColumnsToContents()
