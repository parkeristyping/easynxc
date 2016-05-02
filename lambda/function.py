from __future__ import print_function
from __future__ import unicode_literals

import json
import urllib
import boto3
import youtube_dl
import io
import sys
import re

def lambda_handler(event, context = {}):
    s3Resource = boto3.resource('s3')
    s3Client = boto3.client('s3')
    url = event["url"]
    bucket = "easynxc.com"
    key = "songs/{0}.wav".format(re.split('/', event["url"])[-1])
    objs = list(s3Resource.Bucket(bucket).objects.filter(Prefix=key))

    if not len(objs) > 0:
        ydl_opts = {
            'extract_audio': True,
            'audio_format': 'wav',
            'outtmpl': '-'
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            f = io.BytesIO()
            sys.stdout = f
            ydl.download([url])
            s3Resource.Object(bucket, key).put(
                ACL='public-read',
                Body=f.getvalue(),
                Metadata={
                    "url": url
                }
            )

    s3_url = s3Client.generate_presigned_url('get_object', Params = {'Bucket': bucket, 'Key': key})

    return s3_url
