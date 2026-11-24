import pytest
from langchain_core.documents import Document
from backend.app.services.question_number_service import question_number_service


def test_question_formats_extraction():
    sample_text = """
    Q1. Define probability and sample space.
    
    Q.2) Explain the difference between discrete and continuous random variables.
    
    Question 3: What is the Central Limit Theorem?
    Explain its significance in statistical inference.
    
    Question No. 4. State the properties of the normal distribution curve.
    
    5. What are the normal equations for fitting a straight line using the principle of least squares?
    
    6) Define Type I and Type II errors in hypothesis testing.
    
    In paragraph text, there are 5 equations and 10 variables, which should not match as questions.
    Year 2026 was a great year.
    """
    pages = [Document(page_content=sample_text, metadata={"page": 1})]

    # Test Q1.
    found, text, page, msg = question_number_service.find_question_by_number(pages, 1)
    assert found is True
    assert "Define probability" in text
    assert page == 1

    # Test Q.2)
    found, text, page, msg = question_number_service.find_question_by_number(pages, 2)
    assert found is True
    assert "Explain the difference" in text

    # Test Question 3 (multi-line)
    found, text, page, msg = question_number_service.find_question_by_number(pages, 3)
    assert found is True
    assert "Central Limit Theorem" in text
    assert "significance" in text

    # Test Question No. 4
    found, text, page, msg = question_number_service.find_question_by_number(pages, 4)
    assert found is True
    assert "properties of the normal distribution" in text

    # Test 5.
    found, text, page, msg = question_number_service.find_question_by_number(pages, 5)
    assert found is True
    assert "normal equations for fitting a straight line" in text

    # Test 6)
    found, text, page, msg = question_number_service.find_question_by_number(pages, 6)
    assert found is True
    assert "Type I and Type II errors" in text


def test_missing_question_number():
    sample_text = "Q1. Define mean.\nQ2. Define variance."
    pages = [Document(page_content=sample_text, metadata={"page": 1})]

    found, text, page, msg = question_number_service.find_question_by_number(pages, 99)
    assert found is False
    assert text is None
    assert "Question number 99 was not found in the selected document." in msg


def test_no_false_positives_for_ordinary_numbers():
    sample_text = """
    In Chapter 5, the model achieved 95% accuracy.
    Formula: y = 2x + 5.
    Table 3 shows 4 observations.
    """
    pages = [Document(page_content=sample_text, metadata={"page": 1})]

    found, text, page, msg = question_number_service.find_question_by_number(pages, 5)
    assert found is False
