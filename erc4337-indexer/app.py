from flask import Flask, jsonify, request, render_template # type: ignore
from indexer.models import Session, UserOperation
from indexer.event_listener import EventListener
import threading

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/userops', methods=['GET'])
def get_user_ops():
    session = Session()
    try:
        query = session.query(UserOperation)
        
        # Filter parameters
        sender = request.args.get('sender')
        paymaster = request.args.get('paymaster')
        success = request.args.get('success')
        
        if sender:
            query = query.filter(UserOperation.sender == sender)
        if paymaster:
            query = query.filter(UserOperation.paymaster == paymaster)
        if success is not None:
            query = query.filter(UserOperation.success == (success.lower() == 'true'))
            
        # Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        user_ops = query.order_by(UserOperation.block_number.desc())\
                       .offset((page-1)*per_page)\
                       .limit(per_page)\
                       .all()
        
        return jsonify([{
            'userOpHash': op.user_op_hash,
            'sender': op.sender,
            'paymaster': op.paymaster,
            'nonce': str(op.nonce),
            'success': op.success,
            'actualGasCost': str(op.actual_gas_cost),
            'actualGasUsed': str(op.actual_gas_used),
            'blockNumber': op.block_number,
            'timestamp': op.timestamp
        } for op in user_ops])
    
    finally:
        session.close()

@app.route('/debug')
def debug():
    session = Session()
    try:
        # Récupère toutes les opérations
        ops = session.query(UserOperation).all()
        return jsonify({
            'count': len(ops),
            'operations': [{
                'hash': op.user_op_hash,
                'sender': op.sender,
                'block_number': op.block_number,
                'timestamp': op.timestamp
            } for op in ops]
        })
    finally:
        session.close()

def start_event_listener():
    listener = EventListener()
    listener.listen_to_events()

if __name__ == '__main__':
    # Start the event listener in a separate thread
    listener_thread = threading.Thread(target=start_event_listener)
    listener_thread.daemon = True
    listener_thread.start()
    
    # Start the Flask application
    app.run(debug=True)