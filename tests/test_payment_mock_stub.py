import os
import sys
import pytest
from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway



# ----------------------------------------
# TESTS FOR pay_late_fees()
# ----------------------------------------
def test_pay_late_fees_success(mocker):
    # ---- STUB DB FUNCTIONS ----
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 10.00}
    )
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"title": "Clean Code"}
    )

    # ---- MOCK PAYMENT GATEWAY ----
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_123", "Success")

    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is True
    assert txn == "txn_123"
    assert "Payment successful" in msg

    mock_gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=10.00,
        description="Late fees for 'Clean Code'"
    )


def test_pay_late_fees_payment_declined(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 10.00})
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"title": "Clean Code"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, None, "Card declined")

    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert "Payment failed: Card declined" in msg
    assert txn is None


def test_pay_late_fees_invalid_patron_id():
    mock_gateway = Mock(spec=PaymentGateway)

    success, msg, txn = pay_late_fees("12", 1, mock_gateway)

    assert success is False
    assert txn is None
    mock_gateway.process_payment.assert_not_called()  # REQUIRED


def test_pay_late_fees_zero_fee(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 0})
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"title": "Clean Code"})

    mock_gateway = Mock(spec=PaymentGateway)

    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert "No late fees" in msg
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_gateway_exception(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 10.00})
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"title": "Clean Code"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = Exception("Network failure")

    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert "Payment processing error" in msg
    assert txn is None
# ----------------------------------------
# TESTS FOR refund_late_fee_payment()
# ----------------------------------------
def test_refund_success():
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund successful")

    success, msg = refund_late_fee_payment("txn_54321", 5.00, mock_gateway)

    assert success is True
    assert "Refund successful" in msg

    mock_gateway.refund_payment.assert_called_once_with("txn_54321", 5.00)


def test_refund_invalid_transaction_id():
    mock_gateway = Mock(spec=PaymentGateway)

    success, msg = refund_late_fee_payment("bad123", 5.00, mock_gateway)

    assert success is False
    assert "Invalid transaction ID" in msg
    mock_gateway.refund_payment.assert_not_called()


@pytest.mark.parametrize("invalid_amount", [0, -5, 20])
def test_refund_invalid_amount(invalid_amount):
    mock_gateway = Mock(spec=PaymentGateway)

    success, msg = refund_late_fee_payment("txn_11111", invalid_amount, mock_gateway)

    assert success is False
    assert mock_gateway.refund_payment.called is False
