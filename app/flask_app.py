from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import app.config as config
import app.domain.model as model
import app.adapters.repository as repository
import app.adapters.orm as orm
import app.service_layer.services as services
import app.service_layer.unit_of_work as unit_of_work

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_url()))
app = Flask(__name__)


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    uow = unit_of_work.SqlAlchemyUnitOfWork(get_session)

    try:
        batchref = services.allocate(
            request.json["orderid"],
            request.json["sku"],
            request.json["qty"],
            uow
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({"message": str(e)}), 400

    return jsonify({"batchref": batchref}), 201


@app.route("/add_batch", methods=["POST"])
def add_batch_endpoint():
    uow = unit_of_work.SqlAlchemyUnitOfWork(get_session)

    eta = datetime.fromisoformat(request.json["eta"]) if request.json["eta"] else None

    services.add_batch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        eta,
        uow
    )
    return "OK", 201
