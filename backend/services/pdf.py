from pypdf import PdfReader


def extract_pdf_text(file) -> str:
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def chunk_text(text: str, max_chars: int = 1800) -> list[str]:
    """
    Splits text into roughly max_chars chunks on paragraph boundaries when possible.
    """
    if not text:
        return []

    paras = [p.strip() for p in text.split("\n") if p.strip()]
    chunks: list[str] = []
    buf = ""

    for p in paras:
        if len(buf) + len(p) + 1 <= max_chars:
            buf = (buf + "\n" + p).strip() if buf else p
        else:
            if buf:
                chunks.append(buf)
            buf = p

    if buf:
        chunks.append(buf)

    return chunks


def pick_spread_chunks(chunks: list[str], max_chunks: int = 4) -> list[str]:
    """
    Picks chunks spread across the document (start/middle/end) to cover more content.
    """
    if not chunks:
        return []

    if len(chunks) <= max_chunks:
        return chunks

    idxs = [round(i * (len(chunks) - 1) / (max_chunks - 1)) for i in range(max_chunks)]
    idxs = sorted(set(idxs))
    return [chunks[i] for i in idxs]
