"""Route handlers."""

from flask import Blueprint, render_template, request, jsonify

from app.ical_generator import DAYS, HOURS, generate_ical
import bospy.bos as bos
import bospy.run as run


main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Render the main calendar interface."""
    return render_template('index.html', days=DAYS, hours=HOURS)


@main.route('/locations', methods=['GET'])
def locations():
    """Return all available locations."""
    all_locations = bos.GetAllLocation()
    return jsonify(sorted(all_locations))


@main.route('/submit', methods=['POST'])
def submit():
    """
    Generate iCalendar and save to Redis via bospy.
    
    Expects JSON: {
        "space_name": "Conference Room A",
        "selections": {"Monday": [{"hour": 9, "minute": 0}, ...], ...}
    }
    
    Returns JSON: {
        "ical": "BEGIN:VCALENDAR...",
        "message": "Schedule saved",
        "redis_key": "global:{space_name}:schedule"
    }
    """
    data = request.get_json()
    space_name = data.get('space_name', 'Space')
    selections = data.get('selections', {})
    
    ical_string = generate_ical(selections, space_name)
    
    # Write to Redis via bospy
    key = f"global:{space_name}_schedule"
    run.Set(key, ical_string)
    
    return jsonify({
        'ical': ical_string,
        'message': 'Schedule saved',
        'redis_key': key
    })