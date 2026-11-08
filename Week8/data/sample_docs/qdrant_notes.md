# Qdrant notes

Qdrant is a vector database. Data lives in collections of points; each point has a vector and a JSON payload used to store the text and metadata.

Qdrant supports cosine, dot product and Euclidean distance. The collection's vector size must equal the embedding model's dimension, and the same embedding model must be used for indexing and querying.

Payload filters let you restrict a similarity search by metadata such as source file or tenant.
