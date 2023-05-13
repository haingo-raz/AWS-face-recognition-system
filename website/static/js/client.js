$(document).ready(function() {

  $('#studentTable').DataTable({
    "pagingType": "full_numbers" // add pagination
  });

  $('#myTable').DataTable({
    "pageLength": 10
  });

  var table = $('.attendancetable').DataTable();

  // Iterate over all cells in the table
  table.cells().nodes().to$().each(function() {
    var status = $(this).text().trim().toLowerCase();
    
    // Add class to change cell background color based on the status
    if (status === "present") {
      $(this).addClass("present");
    } else if (status === "absent") {
      $(this).addClass("absent");
    }
  });
});


//Clear form for student registration 
function clearForm() {
    //Access the form by id
    var form = document.getElementById("registrationForm");
    // Reset the form 
    form.reset();
    // Clear the file input field
    var fileInput = document.getElementById("photo");
    fileInput.value = "";
}


//Filter the attendance table by date
//Access the date input
const filterInput = document.getElementById('filter-date');
const rows = document.querySelectorAll('#attendanceTable tbody tr');

filterInput.addEventListener('change', (event) => {

  const selectedDate = event.target.value;

  rows.forEach(row => {
    const dateCell = row.querySelector('td:nth-of-type(2)'); //date is in the second columm 
    const dateString = dateCell.innerText;

    // Convert the date string to a valid ISO format
    const parts = dateString.split(' ');
    const dateParts = parts[0].split('-');
    const timeParts = parts[1].split(':');
    const date = new Date(Date.UTC(dateParts[0], dateParts[1] - 1, dateParts[2], timeParts[0], timeParts[1], timeParts[2]));

    // Format the date as YYYY-MM-DD for comparison with the input value
    const formattedDate = date.toISOString().substr(0, 10);

    if (formattedDate === selectedDate) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
});


//Get FaceID based on given ExternalImageID
function getFaceId() {
  //get the selected input value === face ID
  var faceId = document.getElementById('student_name').selectedOptions[0].value;
  //get the selected input value text == name of the student 
  var personName = document.getElementById('student_name').selectedOptions[0].text;

  //access the studentname input
  var name_input = document.getElementById('studentname');

 //access the face_id text input
  var id_input = document.getElementById('face_id');

  //change the value of the input text to the value of the selected option
  id_input.value = faceId;
  name_input.value = personName;

}




  
  
  
  