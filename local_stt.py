import whisper

_model = None

def _load_model():
    global _model
    print("Loading Whisper ASR model (large-v3)...")
    _model = whisper.load_model("base")
    print("Model loaded.")


def stt_from_file(path: str) -> str:
    """
    path -> text (highest accuracy, short audio)
    """
    global _model
    assert _model is not None, "Model not loaded; call _load_model() first"
    result = _model.transcribe(
        path,
        language="he",      # set if known, improves accuracy
        temperature=0.0,    # no guessing
        fp16=True           # GPU; set False if CPU
    )
    return result["text"].strip()
