import re
import logging
from typing import List, Optional, Tuple, Dict, Any
from langchain_core.documents import Document

logger = logging.getLogger("documind.question_number")


class QuestionNumberService:
    def __init__(self):
        # Patterns to match at the beginning of a line or after newline
        # Group 1: question number
        self.question_header_patterns = [
            # Q1. / Q.1. / Q1) / Q.1) / Q 1. / Q1:
            re.compile(r"(?:^|\n)\s*(?:Q\.?|Question\s*(?:No\.?)?)\s*(\d+)\s*[:\.\)]\s*(.+)", re.IGNORECASE),
            # 1. / 1) / 1: (when at start of line followed by capital letter or word)
            re.compile(r"(?:^|\n)\s*(\d+)\s*[\.\):]\s+([A-Z0-9\"\'\`].+)", re.MULTILINE),
        ]

    def extract_all_questions_from_pages(self, pages: List[Document]) -> List[Dict[str, Any]]:
        """
        Extracts all identifiable numbered questions across all document pages.
        Returns a list of dicts:
        {
            "number": int,
            "text": str,
            "page": int,
            "raw_match": str
        }
        """
        questions: List[Dict[str, Any]] = []

        for page in pages:
            page_num = page.metadata.get("page", 1)
            # PyPDFLoader usually reports 0-indexed page numbers, convert to 1-indexed for users
            if isinstance(page_num, int) and page_num == 0:
                page_num = 1
            elif isinstance(page_num, int) and page_num > 0:
                pass  # Already 1-indexed or normal

            text = page.page_content
            lines = text.split("\n")

            current_q_num: Optional[int] = None
            current_q_lines: List[str] = []
            current_page = page_num

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    if current_q_num is not None:
                        current_q_lines.append("")
                    continue

                matched = False
                # Try explicit Q patterns first
                m_q = re.match(r"^\s*(?:Q\.?|Question\s*(?:No\.?)?)\s*(\d+)\s*[:\.\)]\s*(.*)", stripped, re.IGNORECASE)
                if m_q:
                    # Flush previous question
                    if current_q_num is not None and current_q_lines:
                        q_text = " ".join([l.strip() for l in current_q_lines if l.strip()])
                        questions.append({
                            "number": current_q_num,
                            "text": q_text,
                            "page": current_page,
                        })
                    current_q_num = int(m_q.group(1))
                    current_q_lines = [m_q.group(2).strip()] if m_q.group(2).strip() else []
                    current_page = page_num
                    matched = True
                else:
                    # Try numbered list pattern: e.g. "1. What is..." or "1) Define..."
                    m_num = re.match(r"^(\d+)\s*[\.\):]\s+([A-Z0-9\"\'\`].*)", stripped)
                    if m_num:
                        # Ensure this is not a citation like "1. Smith et al." or footnote unless it's a question
                        num_val = int(m_num.group(1))
                        # Flush previous question
                        if current_q_num is not None and current_q_lines:
                            q_text = " ".join([l.strip() for l in current_q_lines if l.strip()])
                            questions.append({
                                "number": current_q_num,
                                "text": q_text,
                                "page": current_page,
                            })
                        current_q_num = num_val
                        current_q_lines = [m_num.group(2).strip()]
                        current_page = page_num
                        matched = True

                if not matched and current_q_num is not None:
                    # Check if line looks like an answer or section header that ends the question
                    if re.match(r"^(?:Ans|Answer|Solution|Note|Hint|Section|Chapter)\s*[:\.]", stripped, re.IGNORECASE):
                        q_text = " ".join([l.strip() for l in current_q_lines if l.strip()])
                        questions.append({
                            "number": current_q_num,
                            "text": q_text,
                            "page": current_page,
                        })
                        current_q_num = None
                        current_q_lines = []
                    else:
                        # Multi-line question continuation (up to reasonable length)
                        if len(current_q_lines) < 6:
                            current_q_lines.append(stripped)
                        else:
                            # Finished question
                            q_text = " ".join([l.strip() for l in current_q_lines if l.strip()])
                            questions.append({
                                "number": current_q_num,
                                "text": q_text,
                                "page": current_page,
                            })
                            current_q_num = None
                            current_q_lines = []

            # Flush any trailing question on page
            if current_q_num is not None and current_q_lines:
                q_text = " ".join([l.strip() for l in current_q_lines if l.strip()])
                questions.append({
                    "number": current_q_num,
                    "text": q_text,
                    "page": current_page,
                })

        return questions

    def find_question_by_number(self, pages: List[Document], target_num: int) -> Tuple[bool, Optional[str], Optional[int], Optional[str]]:
        """
        Locates target_num in the document pages.
        Returns:
            (found, detected_question_text, page_number, message)
        """
        all_questions = self.extract_all_questions_from_pages(pages)
        matches = [q for q in all_questions if q["number"] == target_num]

        if not matches:
            # Fallback scan for single specific target_num across full document text
            fallback_res = self._fallback_scan(pages, target_num)
            if fallback_res:
                return True, fallback_res["text"], fallback_res["page"], None

            msg = f"Question number {target_num} was not found in the selected document."
            return False, None, None, msg

        # Pick the most complete question text match
        best_match = max(matches, key=lambda m: len(m["text"]))
        detected_text = best_match["text"].strip()
        
        # If detected text is too short (e.g. just a header with text on next line)
        if len(detected_text) < 5:
            detected_text = f"Question {target_num}"

        return True, detected_text, best_match["page"], None

    def _fallback_scan(self, pages: List[Document], target_num: int) -> Optional[Dict[str, Any]]:
        """
        Targeted regex scan for target_num if general line parsing missed it.
        """
        patterns = [
            re.compile(rf"(?:^|\n)\s*(?:Q\.?|Question\s*(?:No\.?)?)\s*{target_num}\s*[:\.\)]\s*(.+?)(?=\n\s*(?:Q\.?|Question|\d+[\.\)]|Ans|$))", re.IGNORECASE | re.DOTALL),
            re.compile(rf"(?:^|\n)\s*{target_num}\s*[\.\):]\s+([A-Z0-9\"\'\`].+?)(?=\n\s*(?:\d+[\.\)]|Ans|$))", re.DOTALL),
        ]

        for page in pages:
            page_num = page.metadata.get("page", 1)
            text = page.page_content
            for p in patterns:
                m = p.search(text)
                if m:
                    extracted = " ".join([l.strip() for l in m.group(1).split("\n") if l.strip()])
                    if extracted:
                        return {"number": target_num, "text": extracted[:300], "page": page_num}
        return None


question_number_service = QuestionNumberService()
