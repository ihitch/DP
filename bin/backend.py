import motor.motor_tornado
import multiprocessing as mp
import pickle
import pymongo



class Backend():
	def __init__(self):
		pass

	def initialize(self):
		pass

	async def workflow_query(self, page, page_size):
		raise NotImplementedError()

	async def workflow_create(self, workflow):
		raise NotImplementedError()

	async def workflow_get(self, id):
		raise NotImplementedError()

	async def workflow_update(self, id, workflow):
		raise NotImplementedError()

	async def workflow_delete(self, id):
		raise NotImplementedError()

	async def task_query(self, page, page_size):
		raise NotImplementedError()

	async def task_create(self, task):
		raise NotImplementedError()

	async def task_get(self, id):
		raise NotImplementedError()


class MongoBackend(Backend):
	def __init__(self, url):
		self._url = url
		self.initialize()

	def initialize(self):
		self._client = motor.motor_tornado.MotorClient(self._url)
		self._db = self._client['nextflow_api']

	async def workflow_query(self, page, page_size):
		return await self._db.workflows \
			.find() \
			.sort('date_created', pymongo.DESCENDING) \
			.skip(page * page_size) \
			.to_list(length=page_size)

	async def workflow_create(self, workflow):
		return await self._db.workflows.insert_one(workflow)

	async def workflow_get(self, id):
		return await self._db.workflows.find_one({ '_id': id })

	async def workflow_update(self, id, workflow):
		return await self._db.workflows.replace_one({ '_id': id }, workflow)

	async def workflow_delete(self, id):
		return await self._db.workflows.delete_one({ '_id': id })

	async def task_query(self, page, page_size):
		return await self._db.tasks \
			.find({}, { '_id': 1, 'runName': 1, 'utcTime': 1, 'event': 1 }) \
			.sort('utcTime', pymongo.DESCENDING) \
			.skip(page * page_size) \
			.to_list(length=page_size)

	async def task_query_pipelines(self):
		# find all 'started' events
		tasks = await self._db.tasks \
			.find({ 'event': 'started' }, { 'metadata.workflow.projectName': 1 }) \
			.to_list(length=None)

		# extract list of unique pipelines
		pipelines = [t['metadata']['workflow']['projectName'] for t in tasks]
		pipelines = list(set(pipelines))

		return pipelines

	async def task_query_pipeline(self, pipeline):
		# find all runs of the given pipeline
		runs = await self._db.tasks \
			.find({ 'event': 'started', 'metadata.workflow.projectName': pipeline }, { 'runId': 1 }) \
			.to_list(length=None)

		run_ids = [run['runId'] for run in runs]

		# find all tasks associated with the given runs
		tasks = await self._db.tasks \
			.find({ 'event': 'process_completed', 'runId': { '$in': run_ids } }) \
			.to_list(length=None)

		return tasks

	async def task_create(self, task):
		return await self._db.tasks.insert_one(task)

	async def task_get(self, id):
		return await self._db.tasks.find_one({ '_id': id })
