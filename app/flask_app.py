from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.config as config
import app.model as model
import app.repository as repository
import app.orm as orm

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_url()))
app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    batches = repository.SqlAlchemyRepository(session).list()
    line = model.OrderLine(
        request.json["orderid"],
        request.json["sku"],
        request.json["qty"],
    )

    batchref = model.allocate(line, batches)

    return jsonify({"batchref": batchref}), 201
