#!/usr/bin/env python3
import pika
import json
from datetime import datetime as dt
import datetime
import ssl
import pika

local_rabbitmq_server = True # set False to connect to AWS rabbitmq server
ssl_context = None

if not local_rabbitmq_server:
  ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
  ssl_context.set_ciphers('ECDHE+AESGCM:!ECDSA')

url = "amqp://guest:guest@localhost/"

if not local_rabbitmq_server:
  url = f"amqps://distributed_cosim_demo:CONTACT_CLAUDIO@CONTACT_CLAUDIO:5671"

parameters = pika.URLParameters(url)
if ssl_context is not None:
  parameters.ssl_options = pika.SSLOptions(context=ssl_context)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

print("Declaring exchange")
channel.exchange_declare(exchange='cosim_exchange', exchange_type='direct')

cosim_queue = channel.queue_declare(queue='', exclusive=True).method.queue
telegraf_queue = channel.queue_declare(queue="telegraf_queue", exclusive=False).method.queue 

channel.queue_bind(exchange='cosim_exchange', queue=cosim_queue, routing_key='to_tb')

# telegraf queue
channel.queue_bind(exchange='cosim_exchange', queue=telegraf_queue, routing_key='to_tb')
channel.queue_bind(exchange='cosim_exchange', queue=telegraf_queue, routing_key='to_cosim')


print(' [*] Waiting for logs. To exit press CTRL+C: ')

utc_delta = datetime.timedelta(hours=2)
dk_tz = datetime.timezone(utc_delta, name="UTC")
time_0 = dt.now(tz = dk_tz)

def control_loop(ch, method, properties, body):
  global time_0
  print(" [x] %r - %r " % (method.routing_key, body))

  msg_in = json.loads(body)
  
  msg = {}

  # Simulating arduino force measurement response. 
  msg['spring_measure'] = -37.0*msg_in['x'] if 'x' in msg_in else 0.0

  if "internal_status" in msg_in:
    time_0 = dt.now(tz = dk_tz)
    msg['time'] = time_0.isoformat(timespec='milliseconds')
  else:
    assert "simstep" in msg_in
    msg['time'] = (time_0 + datetime.timedelta(milliseconds=float(msg_in["simstep"]))).isoformat(timespec='milliseconds')
    print(msg_in["simstep"])

  msg_json = json.dumps(msg)
  channel.basic_publish(exchange='cosim_exchange', routing_key='to_cosim', body=msg_json)
  print("Sent:")
  print(msg_json)

channel.basic_consume(
    queue=cosim_queue, on_message_callback=control_loop, auto_ack=True)

channel.start_consuming()
connection.close()
