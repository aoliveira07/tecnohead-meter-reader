from pathlib import Path


ROOT = Path(__file__).parents[2]
FIRMWARE = (ROOT / "firmware" / "tecnohead-meter-reader.yaml").read_text(encoding="utf-8")


def test_rx_only_contract() -> None:
    assert "number: GPIO16" in FIRMWARE
    assert "tx_pin:" not in FIRMWARE
    assert "\n        - uart.write:" not in FIRMWARE
    assert "dummy_receiver: false" in FIRMWARE
    assert "restore_value: true" in FIRMWARE
    assert "mqtt.publish" not in FIRMWARE


def test_serial_options_are_present() -> None:
    for option in ["300", "600", "1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200"]:
        assert f'"{option}"' in FIRMWARE
    assert 'options: ["Nenhuma", "Par", "Ímpar"]' in FIRMWARE
    assert 'options: ["7", "8"]' in FIRMWARE
    assert 'options: ["1", "2"]' in FIRMWARE
