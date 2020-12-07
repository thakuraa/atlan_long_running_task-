import flask
from threading import Thread
from worker.export import exportWorker
from worker.upload import uploadWorker
from flask_cors import CORS
import uuid
app = flask.Flask(__name__)
app.config["DEBUG"] = False
CORS(app, resources={r"/*": {"origins": "*"}})
global uploadqueue
uploadqueue = {}
global exportqueue
exportqueue = {}
@app.route('/upload', methods=['POST'])
def upload():
    u_id = uuid.uuid4()
    uploadedfile = flask.request.files['teams']
    if uploadedfile.filename != '':
        uploadedfile.save(str(u_id)+"file.csv")
    else:
        return {"Error": "No file uploaded"}
    uploadqueue[u_id] = uploadWorker(u_id) 
    thread = Thread(target = uploadqueue[u_id].start)
    thread.start()
    return {"Task_id": u_id, "Status": "Upload started"}

@app.route('/upload/pause', methods=['POST'])
def uploadpause():
    if "task_id" not in flask.request.form:
        return {"Error": "Missing parameters"}
    task_id = flask.request.form["task_id"]
    if uuid.UUID(task_id) in uploadqueue:
        if uploadqueue[uuid.UUID(task_id)].success:
            return {"Status": "Upload is completed"}
        uploadqueue[uuid.UUID(task_id)].pause()
        return {"Status": "Upload paused"}
    else:
        return {"Error": "No upload task with given id"}

@app.route('/upload/resume', methods=['POST'])
def uploadresume():
    if "task_id" not in flask.request.form:
        return {"Error": "Missing parameters"}
    task_id = flask.request.form["task_id"]
    if uuid.UUID(task_id) in uploadqueue:
        if uploadqueue[uuid.UUID(task_id)].success:
            return {"Status": "Upload is completed"}
        thread = Thread(target = uploadqueue[uuid.UUID(task_id)].resume)
        thread.start()
        return {"Status": "Upload resumed"}
    else:
        return {"Error": "No upload task with given id"}

@app.route('/upload/terminate', methods=['POST'])
def uploadterminate():
    if "task_id" not in flask.request.form:
        return {"Error": "Missing parameters"}
    task_id = flask.request.form["task_id"]
    if uuid.UUID(task_id) in uploadqueue:
        if uploadqueue[uuid.UUID(task_id)].success:
            return {"Status": "Upload is completed"}
        uploadqueue[uuid.UUID(task_id)].terminate()
        del uploadqueue[uuid.UUID(task_id)]
        return {"Status": "Upload terminated"}
    else:
        return {"Error": "No upload task with given id"}

@app.route('/upload/status', methods=['POST'])
def uploadstatus():
    if "task_id" not in flask.request.form:
        return {"Error": "Missing parameters"}
    task_id = flask.request.form["task_id"]
    if uuid.UUID(task_id) in uploadqueue:
        msg = uploadqueue[uuid.UUID(task_id)].status()
        if msg == "Complete":
            del uploadqueue[uuid.UUID(task_id)]
        return {"Status": msg}
    else:
        return {"Error": "No upload task with given id"}
@app.route('/export', methods=['POST'])
def export():
    if "start_date" not in flask.request.form or "end_date" not in flask.request.form:
        return {"Error": "Missing parameters"}
    start_date = flask.request.form["start_date"]
    end_date = flask.request.form["end_date"]
    u_id = uuid.uuid4()
    exportqueue[u_id] = exportWorker(start_date,end_date,u_id) 
    thread = Thread(target = exportqueue[u_id].start)
    thread.start()
    return {"Task_id": u_id, "status": "export started"}

@app.route('/export/pause', methods=['POST'])
def pause_export():
    if "task_id" not in flask.request.form:
        return {"Error": "Missing parameters"}
    task_id = flask.request.form["task_id"]
    if uuid.UUID(task_id) in exportqueue:
        if exportqueue[uuid.UUID(task_id)].success:
            return {"Status": "Export is completed"}
        thread = Thread(target = exportqueue[uuid.UUID(task_id)].resume)
        thread.start()
        exportqueue[uuid.UUID(task_id)].pause()
        return {"Status": "export paused"}
    else:
        return {"Error": "No export task with given id"}

@app.route('/export/resume', methods=['POST'])
def exportresume():
    if "task_id" not in flask.request.form:
        return {"Error": "Missing parameters"}
    task_id = flask.request.form["task_id"]
    if uuid.UUID(task_id) in exportqueue:
        if exportqueue[uuid.UUID(task_id)].success:
            return {"Status": "Export is completed"}
        exportqueue[uuid.UUID(task_id)].resume()
        return {"Status": "export resumed"}
    else:
        return {"Error": "No export task with given id"}

@app.route('/export/terminate', methods=['POST'])
def exportterminate():
    if "task_id" not in flask.request.form:
        return {"Error": "Missing parameters"}
    task_id = flask.request.form["task_id"]
    if uuid.UUID(task_id) in exportqueue:
        if exportqueue[uuid.UUID(task_id)].success:
            return {"Status": "Export is completed"}
        exportqueue[uuid.UUID(task_id)].terminate()
        del exportqueue[uuid.UUID(task_id)]
        return {"Status": "Upload terminated"}
    else:
        return {"Error": "No export task with given id"}

@app.route('/export/status', methods=['POST'])
def exportstatus():
    if "task_id" not in flask.request.form:
        return {"Error": "Missing parameters"}
    task_id = flask.request.form["task_id"]
    if uuid.UUID(task_id) in exportqueue:
        msg = exportqueue[uuid.UUID(task_id)].status()
        if msg == "Complete":
            del exportqueue[uuid.UUID(task_id)]
            response = flask.send_from_directory(directory='./', filename=str(task_id)+"file.csv")
            return response
        return {"Status": msg}
    else:
        return {"Error": "No export task with given id"}

app.run(host = "0.0.0.0")