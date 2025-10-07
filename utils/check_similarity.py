from sentence_transformers import util
from .get_similarity_model import get_similarity_model


def check_similarity(input_text, output_text):
    model = get_similarity_model()
    emb1 = model.encode(input_text, convert_to_tensor=True)
    emb2 = model.encode(output_text, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(emb1, emb2).item()
    return similarity



