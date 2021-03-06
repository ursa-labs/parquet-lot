import json, re, sys
args = json.loads(sys.argv[1].replace('\\"', '"')) if len(sys.argv) > 1 else {}

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder.getOrCreate()
sc = spark.sparkContext

schema = StructType([
    StructField("ByteType_null_ok", ByteType(), True),
    StructField("ByteType_no_null", ByteType(), False),
    StructField("ShortType_null_ok", ShortType(), True),
    StructField("ShortType_no_null", ShortType(), False),
    StructField("IntegerType_null_ok", IntegerType(), True),
    StructField("IntegerType_no_null", IntegerType(), False),
    StructField("LongType_null_ok", LongType(), True),
    StructField("LongType_no_null", LongType(), False),
    StructField("FloatType_null_ok", FloatType(), True),
    StructField("FloatType_no_null", FloatType(), False),
    StructField("DoubleType_null_ok", DoubleType(), True),
    StructField("DoubleType_no_null", DoubleType(), False),
    StructField("DecimalType_38_0_null_ok", DecimalType(38, 0), True),
    StructField("DecimalType_38_0_no_null", DecimalType(38, 0), False),
    StructField("DecimalType_38_38_null_ok", DecimalType(38, 38), True),
    StructField("DecimalType_38_38_no_null", DecimalType(38, 38), False),
    StructField("StringType_null_ok", StringType(), True),
    StructField("StringType_no_null", StringType(), False),
    StructField("BinaryType_null_ok", BinaryType(), True),
    StructField("BinaryType_no_null", BinaryType(), False),
    StructField("BooleanType_null_ok", BooleanType(), True),
    StructField("BooleanType_no_null", BooleanType(), False),
    StructField("TimestampType_null_ok", TimestampType(), True),
    StructField("TimestampType_no_null", TimestampType(), False),
    StructField("DateType_null_ok", DateType(), True),
    StructField("DateType_no_null", DateType(), False)
])

#rows contain:
# 0. bottom of range (for numeric types)
# 1. top of range (for numeric types)
# 2. zero/empty
# 3. negative zero/empty
# 4. null for nullable fields, zero/empty for non-nullable

json = """
[
    {
      "ByteType_null_ok": -128,
      "ByteType_no_null": -128,
      "ShortType_null_ok": -32768,
      "ShortType_no_null": -32768,
      "IntegerType_null_ok": -2147483648,
      "IntegerType_no_null": -2147483648,
      "LongType_null_ok": -9223372036854775808,
      "LongType_no_null": -9223372036854775808,
      "FloatType_null_ok": -3.40282346638528860e+38,
      "FloatType_no_null": -1.40129846432481707e-45,
      "DoubleType_null_ok": -4.94065645841246544e-324,
      "DoubleType_no_null": -1.79769313486231570e+308,
      "DecimalType_38_0_null_ok": -99999999999999999999999999999999999999,
      "DecimalType_38_0_no_null": -99999999999999999999999999999999999999,
      "DecimalType_38_38_null_ok": -0.00000000000000000000000000000000000001,
      "DecimalType_38_38_no_null": -0.00000000000000000000000000000000000001,
      "StringType_null_ok": "\\u0000\\u0001\\u0002\\u0003\\u0004\\u0005\\u0006\\u0007\\b\\t\\n\\u000b\\f\\r\\u000e\\u000f\\u0010\\u0011\\u0012\\u0013\\u0014\\u0015\\u0016\\u0017\\u0018\\u0019\\u001a\\u001b\\u001c\\u001d\\u001e\\u001f !\\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\\u007f",
      "StringType_no_null": "\\u0000\\u0001\\u0002\\u0003\\u0004\\u0005\\u0006\\u0007\\b\\t\\n\\u000b\\f\\r\\u000e\\u000f\\u0010\\u0011\\u0012\\u0013\\u0014\\u0015\\u0016\\u0017\\u0018\\u0019\\u001a\\u001b\\u001c\\u001d\\u001e\\u001f !\\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\\u007f",
      "BinaryType_null_ok": "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w==",
      "BinaryType_no_null": "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w==",
      "BooleanType_null_ok": false,
      "BooleanType_no_null": false,
      "TimestampType_null_ok": "0001-01-01T00:00:00.000000-00:00",
      "TimestampType_no_null": "0001-01-01T00:00:00.000000-00:00",
      "DateType_null_ok": "0001-01-01",
      "DateType_no_null": "0001-01-01"
    },
    {
      "ByteType_null_ok": 127,
      "ByteType_no_null": 127,
      "ShortType_null_ok": 32767,
      "ShortType_no_null": 32767,
      "IntegerType_null_ok": 2147483647,
      "IntegerType_no_null": 2147483647,
      "LongType_null_ok": 9223372036854775807,
      "LongType_no_null": 9223372036854775807,
      "FloatType_null_ok": 3.40282346638528860e+38,
      "FloatType_no_null": 1.40129846432481707e-45,
      "DoubleType_null_ok": 4.94065645841246544e-324,
      "DoubleType_no_null": 1.79769313486231570e+308,
      "DecimalType_38_0_null_ok": 99999999999999999999999999999999999999,
      "DecimalType_38_0_no_null": 99999999999999999999999999999999999999,
      "DecimalType_38_38_null_ok": 0.00000000000000000000000000000000000001,
      "DecimalType_38_38_no_null": 0.00000000000000000000000000000000000001,
      "StringType_null_ok": "\\u0000\\u0001\\u0002\\u0003\\u0004\\u0005\\u0006\\u0007\\b\\t\\n\\u000b\\f\\r\\u000e\\u000f\\u0010\\u0011\\u0012\\u0013\\u0014\\u0015\\u0016\\u0017\\u0018\\u0019\\u001a\\u001b\\u001c\\u001d\\u001e\\u001f !\\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\\u007f",
      "StringType_no_null": "\\u0000\\u0001\\u0002\\u0003\\u0004\\u0005\\u0006\\u0007\\b\\t\\n\\u000b\\f\\r\\u000e\\u000f\\u0010\\u0011\\u0012\\u0013\\u0014\\u0015\\u0016\\u0017\\u0018\\u0019\\u001a\\u001b\\u001c\\u001d\\u001e\\u001f !\\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\\u007f",
      "BinaryType_null_ok": "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w==",
      "BinaryType_no_null": "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w==",
      "BooleanType_null_ok": true,
      "BooleanType_no_null": true,
      "TimestampType_null_ok": "9999-12-31T23:59:59.999999-00:00",
      "TimestampType_no_null": "9999-12-31T23:59:59.999999-00:00",
      "DateType_null_ok": "9999-12-31",
      "DateType_no_null": "9999-12-31"
    },
    {
      "ByteType_null_ok": 0,
      "ByteType_no_null": 0,
      "ShortType_null_ok": 0,
      "ShortType_no_null": 0,
      "IntegerType_null_ok": 0,
      "IntegerType_no_null": 0,
      "LongType_null_ok": 0,
      "LongType_no_null": 0,
      "FloatType_null_ok": 0.0,
      "FloatType_no_null": 0.0,
      "DoubleType_null_ok": 0.0,
      "DoubleType_no_null": 0.0,
      "DecimalType_38_0_null_ok": 0,
      "DecimalType_38_0_no_null": 0,
      "DecimalType_38_38_null_ok": 0.0,
      "DecimalType_38_38_no_null": 0.0,
      "StringType_null_ok": "",
      "StringType_no_null": "",
      "BinaryType_null_ok": "",
      "BinaryType_no_null": "",
      "BooleanType_null_ok": false,
      "BooleanType_no_null": false,
      "TimestampType_null_ok": "0001-01-01T00:00:00.000000-00:00",
      "TimestampType_no_null": "0001-01-01T00:00:00.000000-00:00",
      "DateType_null_ok": "0001-01-01",
      "DateType_no_null": "0001-01-01"
    },
    {
      "ByteType_null_ok": -0,
      "ByteType_no_null": -0,
      "ShortType_null_ok": -0,
      "ShortType_no_null": -0,
      "IntegerType_null_ok": -0,
      "IntegerType_no_null": -0,
      "LongType_null_ok": -0,
      "LongType_no_null": -0,
      "FloatType_null_ok": -0.0,
      "FloatType_no_null": -0.0,
      "DoubleType_null_ok": -0.0,
      "DoubleType_no_null": -0.0,
      "DecimalType_38_0_null_ok": -0,
      "DecimalType_38_0_no_null": -0,
      "DecimalType_38_38_null_ok": -0.0,
      "DecimalType_38_38_no_null": -0.0,
      "StringType_null_ok": "",
      "StringType_no_null": "",
      "BinaryType_null_ok": "",
      "BinaryType_no_null": "",
      "BooleanType_null_ok": false,
      "BooleanType_no_null": false,
      "TimestampType_null_ok": "0001-01-01T00:00:00.000000-00:00",
      "TimestampType_no_null": "0001-01-01T00:00:00.000000-00:00",
      "DateType_null_ok": "0001-01-01",
      "DateType_no_null": "0001-01-01"
    },
    {
      "ByteType_null_ok": null,
      "ByteType_no_null": 0,
      "ShortType_null_ok": null,
      "ShortType_no_null": 0,
      "IntegerType_null_ok": null,
      "IntegerType_no_null": 0,
      "LongType_null_ok": null,
      "LongType_no_null": 0,
      "FloatType_null_ok": null,
      "FloatType_no_null": 0.0,
      "DoubleType_null_ok": null,
      "DoubleType_no_null": 0.0,
      "DecimalType_38_0_null_ok": null,
      "DecimalType_38_0_no_null": 0,
      "DecimalType_38_38_null_ok": null,
      "DecimalType_38_38_no_null": 0.0,
      "StringType_null_ok": null,
      "StringType_no_null": "",
      "BinaryType_null_ok": null,
      "BinaryType_no_null": "",
      "BooleanType_null_ok": null,
      "BooleanType_no_null": false,
      "TimestampType_null_ok": null,
      "TimestampType_no_null": "0001-01-01T00:00:00.000000-00:00",
      "DateType_null_ok": null,
      "DateType_no_null": "0001-01-01"
    }
]
"""

data = spark.read.schema(schema).json(sc.parallelize([json]))
# data.show() # for debugging

task_name = args.get('task_name') or 'task'
comps = args.get('compression') or ['none']

for comp in comps:
    file = 'artifacts/' + task_name + '_' + spark.version + '_' + comp
    data.repartition(1).write.parquet(file, compression = comp)

spark.stop()

json_out = json.strip().lstrip('[').rstrip(']').strip()
subs = (('\s*},\s*\n\s*{\s*', '}\n{'), (',\n\s*', ', '), ('{\s+', '{'), ('\s+}', '}'))
for sub in subs:
    json_out = re.sub(sub[0], sub[1], json_out)
json_out = json_out + '\n'

with open('artifacts/' + task_name + '_' + 'reference.json', 'w') as ref:
    ref.write(json_out)
