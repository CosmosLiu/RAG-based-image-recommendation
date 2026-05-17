from pymilvus import MilvusClient, DataType, AnnSearchRequest, WeightedRanker

class MilvusModel(object):
    def __init__(self, uri="http://localhost:19530", db_name="default", collection_name="image_rag", auto_create=False, load_collection=True):
        self.client = MilvusClient(uri=uri, db_name=db_name)
        self.collection_name = collection_name
        if self.client.has_collection(self.collection_name) is False and auto_create is True:
            self.create_collection()
        if load_collection is True:
            self.load_collection()

    def _create_schema(self):
        schema = self.client.create_schema(auto_id=True)
        schema.add_field(field_name='id', datatype=DataType.INT64, is_primary=True, description='主键id')
        schema.add_field(field_name='uid', datatype=DataType.VARCHAR, max_length=64, description='用户唯一标识')
        # 修改为 512 避免 URL 过长报错
        schema.add_field(field_name='image_id', datatype=DataType.VARCHAR, max_length=512, description='图片标识/URL')
        schema.add_field(field_name='visible_context', datatype=DataType.VARCHAR, max_length=500, description='显性特征关键词')
        schema.add_field(field_name='visible_context_vector', datatype=DataType.FLOAT_VECTOR, dim=1024, description='显性特征关键词向量')
        schema.add_field(field_name='hidden_context', datatype=DataType.VARCHAR, max_length=500, description='隐性特征关键词')
        schema.add_field(field_name='hidden_context_vector', datatype=DataType.FLOAT_VECTOR, dim=1024, description='隐性特征关键词向量')
        schema.add_field(field_name='description', datatype=DataType.VARCHAR, max_length=2000, description='图片描述')
        schema.add_field(field_name='description_vector', datatype=DataType.FLOAT_VECTOR, dim=1024, description='图片描述向量')
        return schema

    def create_collection(self):
        self.client.create_collection(collection_name=self.collection_name, schema=self._create_schema())
        index_params = self.client.prepare_index_params()
        index_params.add_index(field_name='uid', index_type="AUTOINDEX")
        index_params.add_index(field_name='image_id', index_type="AUTOINDEX")
        index_params.add_index(field_name='visible_context_vector', index_type="AUTOINDEX", metric_type="COSINE")
        index_params.add_index(field_name='hidden_context_vector', index_type="AUTOINDEX", metric_type="COSINE")
        index_params.add_index(field_name='description_vector', index_type="AUTOINDEX", metric_type="COSINE")
        self.client.create_index(collection_name=self.collection_name, index_params=index_params, sync=False)

    def load_collection(self):
        self.client.load_collection(collection_name=self.collection_name)

    def drop_collection(self):
        self.client.drop_collection(collection_name=self.collection_name)

    def check_exists(self, uid, image_id):
        try:
            result = self.client.query(
                collection_name=self.collection_name,
                filter=f"uid == '{uid}' && image_id == '{image_id}'",
                output_fields=["id"],
                limit=1
            )
            return len(result) > 0
        except Exception as e:
            print(f"检查数据是否存在时出错: {e}")
            return False

    def insert_data(self, data):
        return self.client.insert(collection_name=self.collection_name, data=data)

    def search(self, uid, docs, topk):
        search_param = {"metric_type": "COSINE", "params": {}}
        search_limit = topk * 3 

        req_visible = AnnSearchRequest(
            data=[docs['visible']['vector']],
            anns_field="visible_context_vector",
            param=search_param,
            limit=search_limit
        )
        req_hidden = AnnSearchRequest(
            data=[docs['hidden']['vector']],
            anns_field="hidden_context_vector",
            param=search_param,
            limit=search_limit
        )
        req_description = AnnSearchRequest(
            data=[docs['description']['vector']],
            anns_field="description_vector",
            param=search_param,
            limit=search_limit
        )
        
        rerank = WeightedRanker(0.4, 0.2, 0.4)
        result = self.client.hybrid_search(
            collection_name=self.collection_name,
            reqs=[req_visible, req_hidden, req_description],
            ranker=rerank,
            limit=search_limit,
            filter=f"uid == '{uid}'",
            output_fields=["uid", "image_id"]
        )

        filtered_results = [
            i['entity'] for i in result[0]
            if i['entity'].get('uid') == uid
        ][:topk]

        return filtered_results
