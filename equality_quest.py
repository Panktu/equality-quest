import sys
import json
import random
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QRadioButton, QMessageBox, QButtonGroup, QLineEdit
)
from fpdf import FPDF

class EqualityQuest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Equality Quest - Gender Equality Awareness Quiz")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.player_name = ""
        self.score = 0
        self.current_question = 0
        self.answers = []

        self.name_label = QLabel("Enter your name to start the quiz:")
        self.name_input = QLineEdit()
        self.start_button = QPushButton("Start Quiz")
        self.start_button.clicked.connect(self.start_quiz)

        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.start_button)

    def start_quiz(self):
        self.player_name = self.name_input.text().strip()
        if not self.player_name:
            QMessageBox.warning(self, "Input Error", "Please enter your name to continue.")
            return

        try:
            with open("questions.json", "r", encoding="utf-8") as f:
                self.all_questions = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "File Error", f"Failed to load questions.json: {str(e)}")
            return

        self.selected_questions = random.sample(self.all_questions, 10)
        self.current_question = 0
        self.score = 0
        self.answers = []

        self.clear_layout()
        self.load_question()

    def clear_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def load_question(self):
        if self.current_question >= len(self.selected_questions):
            self.show_result()
            return

        question_data = self.selected_questions[self.current_question]

        self.question_label = QLabel(f"Q{self.current_question + 1}: {question_data['question']}")
        self.layout.addWidget(self.question_label)

        self.button_group = QButtonGroup(self)
        self.options = []

        for i, option in enumerate(question_data['options']):
            btn = QRadioButton(option)
            self.layout.addWidget(btn)
            self.button_group.addButton(btn)
            self.options.append(btn)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.check_answer)
        self.layout.addWidget(self.next_button)

    def check_answer(self):
        selected_button = self.button_group.checkedButton()
        if not selected_button:
            QMessageBox.warning(self, "No selection", "Please select an option.")
            return

        selected_text = selected_button.text()
        correct_text = self.selected_questions[self.current_question]['answer']

        self.answers.append({
            "question": self.selected_questions[self.current_question]['question'],
            "selected": selected_text,
            "correct": correct_text,
            "supportive": selected_text == correct_text
        })

        if selected_text == correct_text:
            self.score += 1

        self.current_question += 1
        self.clear_layout()
        self.load_question()

    def show_result(self):
        result_label = QLabel(f"Quiz Completed!\n{self.player_name}'s Score: {self.score}/10")
        self.layout.addWidget(result_label)

        for ans in self.answers:
            summary = f"Q: {ans['question']}\nYour Answer: {ans['selected']}\nCorrect: {ans['correct']}\n"
            self.layout.addWidget(QLabel(summary))

        export_button = QPushButton("Export Report to PDF")
        export_button.clicked.connect(self.export_pdf)
        self.layout.addWidget(export_button)

    def export_pdf(self):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Equality Quest - Quiz Report", ln=True, align='C')

            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Player: {self.player_name}", ln=True)
            pdf.cell(200, 10, txt=f"Score: {self.score}/10", ln=True)
            pdf.ln(5)

            for i, ans in enumerate(self.answers, 1):
                result = "Supportive" if ans["supportive"] else "Stereotypical"
                pdf.multi_cell(0, 10, f"Q{i}: {ans['question']}\nYour Answer: {ans['selected']}\nCorrect: {ans['correct']} - {result}\n")

            pdf.ln(10)
            pdf.set_font("Arial", 'I', 11)
            pdf.multi_cell(0, 10, "Thank you for participating in promoting gender equality awareness!\nStay informed. Stay fair.")

            output_path = os.path.join(os.path.expanduser("~"), "Downloads", "equality_report.pdf")
            pdf.output(output_path)

            QMessageBox.information(self, "PDF Saved", f"PDF report saved successfully to:\n{output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export PDF: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EqualityQuest()
    window.show()
    sys.exit(app.exec_())