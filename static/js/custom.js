function selectSeat(id) 
{
    var seat = document.getElementById(id);
    if (seat.src == '/static/images/seat_empty.png') {
        seat.src = '/static/images/seat_male.png';
        document.getElementById('seats').innerHTML += "X";
    }
    else if (seat.src == '/static/images/seat_male.png') {
        seat.src = '/static/images/seat_female.png';
        document.getElementById('seats').innerHTML += "X";
    }
    else {
        seat.src = '/static/images/seat_empty.png';
        document.getElementById('seats').innerHTML = "Y";
    }
}