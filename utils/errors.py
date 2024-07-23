import logging


class DataBaseError(Exception):
    def __init__(self, e: Exception, logger: logging.Logger):
        super().__init__(e)
        logger.error(f"DataBaseError: failed create database | {e}")


class TableValueError(Exception):
    """
    主要处理数据库中不存在表的错误
    """
    def __init__(self, e: Exception, info: str, logger: logging.Logger):
        super().__init__(e)
        logger.error(info)

class TableExportError(Exception):
    def __init__(self, e: Exception, error_type: str, logger: logging.Logger):
        super().__init__(e)
        logger.error(f"TableExportError: failed export table | {error_type}")

class TableNameError(Exception):
    def __init__(self, e: Exception, name: str, logger: logging.Logger):
        super().__init__(e)
        logger.error(f"TableNameError: failed access table: {name} | {e}")


class TableKeyError(Exception):
    def __init__(self, e: Exception, keyname, logger: logging.Logger):
        super().__init__(e)
        logger.error(f"TableAccessError: no key {keyname}")


class TableOperationError(Exception):
    def __init__(self, e: Exception,operator: str, logger: logging.Logger):
        super().__init__(e)
        logger.error(f"TableOperationError: failed operator {operator} | {e}")