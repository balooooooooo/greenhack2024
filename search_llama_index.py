from pprint import pprint
from llama_index.core import Document
from llama_index.core.schema import MetadataMode, TextNode
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import pandas as pd
import transformers.utils.versions
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core import StorageContext, load_index_from_storage

import logging
from typing import List, Dict, Tuple
import os.path

logger = logging.getLogger("Search Llama")
logging.basicConfig(level=logging.INFO)


class KnowledgeBase:
    """
    Wraps and processes the knowledge base.
    """
    def __init__(self):
        self.df = pd.read_excel('dataset.xlsx', sheet_name='ideas')
        self.df['text_idea'] = self.df['name'] + ' ' + self.df['introduction']
    def as_list(self):
        """
        Flattens the dict to a list.
        Each entry is concatenated key+value (question+answer)
        """
        return list(self.df['text_idea'])

    def print(self):
        print(self.dataset_dict)


class VectorDatabase:
    """
    Handles logic about the vector database that stores embeddings.
    """
    index = None

    def build_index(self, strings: List[str]):
        """
        Builds the index. Uses the previous defined model to create the embeddings.
        """

        # Create nodes - Here we can include more information in each node for better filtering
        nodes = [TextNode(text=k) for k in strings]
        self.index = VectorStoreIndex(nodes)

    def get_retriever(self):
        """
        To retrieve the most similar nodes based on a query, we need to
        
        """
        return self.index.as_retriever(retriever_mode="llms", similarity_top_k=10,)

    def save_locally(self):
        self.index.storage_context.persist(persist_dir="./index_storage")

    def load_local(self):
        storage_context = StorageContext.from_defaults(persist_dir="./index_storage")
        self.index = load_index_from_storage(storage_context)


if __name__ == "__main__":
    # Load the knowledge base
    knowledge_base = KnowledgeBase()

    # Define the embeddings model
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/LaBSE"
    )

    index_wrap = VectorDatabase()

    if not os.path.exists("./index_storage"):
        # build the index using the embeddings model
        knowledge_base_list = knowledge_base.as_list()
        index_wrap.build_index(knowledge_base_list)
        index_wrap.save_locally()

    else:
        # load the existing index
        index_wrap.load_local()

    # Get the retriever object
    retriever = index_wrap.get_retriever()
    prompt = "VR headset"
    # Get the most similar texts
    nodes = retriever.retrieve(prompt)

    top_3 = []

    for node in nodes:
        print(f"Score: {node.score} Text:  {node.node.get_text()}")
        top_3.append(node.node.get_text())