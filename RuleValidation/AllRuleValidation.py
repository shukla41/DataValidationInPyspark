from pyspark.sql.functions import col
from pyspark.sql import functions as f
import  numpy as np
from pyspark.sql import Row
from session import ConnctSession
import time
import datetime
import csv
from OutputFileWriter import fileWriter
from pyspark.sql.types import IntegerType
from RuleValidation import ErrorFileMessage

class AttributeValidate:

    def chkNull(attribute, data, metadaDF, inComingRule):
        metadata = metadaDF.where(col("Attribute_Name") == attribute)
        dp = data.where(col(attribute).isNull()).select(col(attribute), col("ID"))
        validation = dp.crossJoin(metadata)
        cnt = validation.where(validation.Table_Primary_Key.isNotNull()).count()
        if cnt > 0:
            action = 'Reject'
            ErrCd = 'ER6'
            ErrMsg = attribute[0] + 'cloumn has null Value'
            ErrVal = 'null'
            err = ErrorFileMessage.ErrorDetection.errorMessege(ErrVal, ErrCd, ErrMsg,action,inComingRule)
            rslt=validation.crossJoin(err)

            rslt.select(col("RunID"),col("Data_Source_Name"),col("Application_Name"),
                        col("Table_Name"),col("Attribute_Name"),col("inComingRule"),col("ID").alias("Primary_key_val"),
                        col("ErrVal"),col("ErrCd"),col("Action"),col("ErrMsg"),col("timeStamp").alias("Run_Timestamp")) \
                 .write.save(path='test.csv', header=True,format='csv', mode='append', sep=',')
        else:
            action = 'warning'
            ErrCd = 'ER6'
            ErrMsg = attribute[0] + 'cloumn has null Value'
            ErrVal = 'null'
            err = ErrorFileMessage.ErrorDetection.errorMessege(ErrVal, ErrCd, ErrMsg,action,inComingRule)
            rslt = validation.crossJoin(err).repartition("ID")

            rslt.select(col("RunID"), col("Data_Source_Name"), col("Application_Name"),
                   col("Table_Name"), col("Attribute_Name"), col("inComingRule"), col("ID").alias("Primary_key_val"),
                   col("ErrVal"), col("ErrCd"), col("Action"), col("ErrMsg"),
                   col("timeStamp").alias("Run_Timestamp")).write.save(path='test.csv', header=True,format='csv', mode='append', sep=',')

           # err.show()
