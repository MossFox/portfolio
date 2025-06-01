/*!
* Start Bootstrap - Simple Sidebar v6.0.6 (https://startbootstrap.com/template/simple-sidebar)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-simple-sidebar/blob/master/LICENSE)
*/
//
// Scripts
//

window.addEventListener('DOMContentLoaded', event => {
    //Automatic class time checker
    //startCheckClassOnHour();

    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        // Uncomment Below to persist sidebar toggle between refreshes
        // if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
        //     document.body.classList.toggle('sb-sidenav-toggled');
        // }
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }
    if (document.getElementById('userLoggedIn')){
        //Checks if the user has notifications
        notification_check()

        notif_board()
    }

    // session clear
    document.querySelector('#refreshButton').addEventListener('click', () => {
        fetch('/clear_session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(() => {
            location.reload();
        })
        .catch(error => console.error('Error:', error));
    });

    // Tracks which club the user choose
    let club = "none";
    document.querySelectorAll('.dropdown-item').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            club = event.target.id;
            console.log(`Club:${club}`);

            document.querySelectorAll('.dropdown-item').forEach(item => {
                item.classList.remove('highlight');
            });

            // Add highlight to the clicked item
            event.target.classList.add('highlight');
            document.querySelector('#navbarDropdown').innerHTML = `${club}`;

            // Send the club variable to the server
            fetch(`/club/${club}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ club: club })
            })
            .then(response => response.json())
            .then(data => {
                document.querySelector('#navbarDropdown').innerHTML = `${club}`;
                // Clear the existing timetable
                let timebox = document.querySelector('.timetable_container');
                if (timebox) {
                    timebox.style.display = 'block'; // Show the timetable container
                    document.querySelector('p').innerHTML = `Welcome to ${club}`;
                    timebox.innerHTML = '';
                }
                location.reload()
            })
            .catch(error => console.error('Error:', error))

        })
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Timetable Page


function timetable(timetables, classes) {

    let container = document.querySelector('.timetable_container'); //selects the existing container on the timetable.html
    const table = document.createElement('table'); //creates a table element
    container.append(table); // adds it to the container
    let tr = document.createElement('tr'); //  creates and adds a table row
    table.append(tr);

    let th = document.createElement('th'); // creates and adds a table heading with title
    th.innerHTML = "Day/Time";
    tr.append(th);

    //creates a list of times
    const time = ["8-9", "9-10", "10-11", "11-12", "12-13", "13-14", "14-15", "15-16", "16-17", "17-18", "18-19", "19-20", "20-21"]

    let i=0;
    while(i < time.length) {
        th = document.createElement('th');
        th.innerHTML =`${time[i]}`;
        tr.append(th);
        i++
    }

    const daysOfWeek = ["Monday", "Tuesday", "Wednsday", "Thursday", "Friday", "Saturday", "Sunday"];
    let q = 0;
    let className = "";
    while (q < daysOfWeek.length) { // while the length of the list is greater than q, keeps running the loop

        tr = document.createElement('tr'); // creates a row
        table.append(tr);
        let td = document.createElement('td'); // creates a segment of the row
        td.innerHTML = `${daysOfWeek[q]}`; // sets it to the corresponding day of the week
        tr.append(td)
        // gets the first 2 letters of the daysofweek[q] item
        let firstLetters = daysOfWeek[q].substring(0, 2);

        let j = 0;
        while( j < time.length) { //while the length of the time list is greater than j
            td = document.createElement('td');
            // gives each td an id number of first 2letters + number j
            td.id = firstLetters + `${j}`;
            td.className = "class_slot";
            // looks up in the timetable data an entry which corresponds with the date and time of the slot
            const entry = timetables.find(t => t.day__day === daysOfWeek[q] && t.slot__time === time[j]);
            if (entry) { // if entry exists sets the inner html to its title
                className = `${entry.name__title}`
                td.innerHTML = `${className}`
                td.setAttribute('data-id', entry.id);
                td.setAttribute('data-capcity', entry.capacity)
                td.setAttribute('data-is-booked', entry.is_booked)
            }
            else {
                td.setAttribute('data-day', daysOfWeek[q]);
                td.setAttribute('data-time', time[j]);
            }
            tr.append(td);
            j++
        }
        q++
    }
    let teacher_check = document.querySelector(".teacher")
    if (teacher_check) {
        teacher_view_listener(classes, timetables);
    } else {
        class_view_listener(classes);
    }
}

function club_choice() {
    let club = "none";
    const selectElement = document.querySelector('.clubz');
    if (selectElement) {
        selectElement.addEventListener('change', (event) => {
            club = event.target.value;
            console.log(`Club: ${club}`);

            document.querySelectorAll('.clubz option').forEach(item => {
                item.classList.remove('highlight');
            });

            // add highlight to the selected option
            event.target.selectedOptions[0].classList.add('highlight');
            fetch(`/club/${club}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ club: club })
            })
            .then(response => response.json())
            .then(data => {
                document.querySelector('#navbarDropdown').innerHTML = `${club}`;
                selectElement.value = club;
                location.reload();
            })
            .catch(error => console.error('Error:', error));
        });
    }
}




function class_view_listener (classes) {
    document.querySelectorAll('.class_slot').forEach(slot => {
        slot.addEventListener('click', function(event) {
            const box = event.target.closest('[data-id]');
            document.querySelectorAll('.class_box').forEach(popup => {
                popup.style.display = 'none';
            });
            if (box) {
                let classBox = document.querySelector('.class_box');
                if (classBox) {
                    classBox.remove();
                }

                let classId = event.target.getAttribute('data-id');
                class_time_check(classId)
                //PH_token(classId)
                let classCap = event.target.getAttribute('data-capcity'); //capacity for this class
                console.log(`People in the class: ${classCap}`)
                let is_booked = event.target.getAttribute('data-is-booked');

                console.log(`Class ID: ${classId}`);

                let className = event.target.innerHTML;

                let slotId = event.target.id;

                // Display popout with details for the clicked slot
                const class_slot = document.querySelector(`#${slotId}`);

                // get the class information based on its name
                let class_info = classes.find(t => t.title === className)
                let teacher = class_info.teacher__username //gets the teacher name

                const class_box = document.createElement('div');
                class_box.className = "class_box";
                let br = document.createElement('br')

                if (teacher != 'admin'){
                    class_box.innerHTML = `${class_info.description}.<br> Taught by ${teacher}.<br> Has capacity of ${class_info.capacity - classCap}.`;

                    document.body.append(class_box);

                    if (is_booked === "false" && classCap < class_info.capacity) {
                        let action = "nothing"
                        class_box.append(br)
                        let button = document.createElement('button');
                        button.type = "submit";
                        button.className = "booking";
                        button.innerHTML = "Book";
                        button.formAction = "book";
                        class_box.append(button);

                        class_box.append(br)
                        let favorites = document.createElement('button');
                        favorites.type = "submit";
                        favorites.className = "favorites";
                        fetch(`/in_favorites/${classId}`, {
                            method: 'GET',
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        })
                        .then(response => response.json())
                        .then(data => {
                            // Handle the response data
                            if (data.fav_status === "add") {
                                button_text = "Add to favorites"
                                favorites.innerHTML = `${button_text}`;

                            }
                            else if (data.fav_status === "remove") {
                                button_text = "Remove from favorites"
                                favorites.innerHTML = `${button_text}`;
                            }
                        })
                        .catch((error) => {
                            console.error('Error:', error);
                        });


                        favorites.formAction = "favorite";
                        class_box.append(favorites);


                        favorites.addEventListener('click', function(event) {
                            event.stopPropagation();
                            favor(classId);
                        });

                        button.addEventListener('click', function(event) {
                            event.stopPropagation();

                            fetch(`/book/${classId}/${action}`, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': getCookie('csrftoken')
                                },
                                body: JSON.stringify({
                                    // send data to the server
                                    className: class_info.title

                                })
                            })
                            .then(response => response.json())
                            .then(data => {
                                // Handle the response data
                                alert('You are booked in');
                                location.reload();

                            })
                            .catch((error) => {
                                console.error('Error:', error);
                            });
                        });
                        pop_pop()
                    }
                    else if (is_booked === "false" && parseInt(classCap) === parseInt(class_info.capacity)) {
                        fetch(`/on_waitinglist/${classId}`, {
                            method: 'GET',
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        })
                        .then(response => response.json())
                        .then(data => {
                            // handles the response data
                            if (data.status === "on_waitlist") {
                                // code to run if user is on the waiting list
                                let full = document.createElement('p')
                                full.innerHTML = "Class is full";
                                class_box.append(full);
                                let que = document.createElement('p')
                                que.innerHTML = `You are number ${data.que_number} on the list`;
                                class_box.append(que)
                                let button = document.createElement('button');
                                button.type = "submit";
                                button.className = "leave";
                                button.innerHTML = "Leave Waitinglist";
                                button.formAction = "leave";
                                let action = "leave";
                                class_box.append(button);

                                let favorites = document.createElement('button');
                                favorites.type = "submit";
                                favorites.className = "favorites";
                                fetch(`/in_favorites/${classId}`, {
                                    method: 'GET',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    }
                                })
                                .then(response => response.json())
                                .then(data => {
                                    // handle the response data
                                    if (data.fav_status === "add") {
                                        button_text = "Add to favorites"
                                        favorites.innerHTML = `${button_text}`;

                                    }
                                    else if (data.fav_status === "remove") {
                                        button_text = "Remove from favorites"
                                        favorites.innerHTML = `${button_text}`;
                                    }
                                })
                                .catch((error) => {
                                    console.error('Error:', error);
                                });
                                class_box.append(favorites);


                                favorites.addEventListener('click', function(event) {
                                    event.stopPropagation();
                                    favor(classId);
                                })

                                button.addEventListener('click', function(event) {
                                    event.stopPropagation();
                                    fetch(`/waitinglist/${classId}/${action}`, {
                                        method: 'POST',
                                        headers: {
                                            'Content-Type': 'application/json',
                                            'X-CSRFToken': getCookie('csrftoken')
                                        },
                                        body: JSON.stringify({
                                            className: class_info.title
                                        })
                                    })
                                    .then(response => response.json())
                                    .then(data => {
                                        if (data.status === "on_waitlist") {
                                            //if user is on the waiting list
                                            alert('You are already on the waitinglist');
                                            location.reload(); //refreshes the page
                                        } else {
                                        alert('You left the waitinglist!');
                                        location.reload(); //refreshes the page
                                        }
                                    })
                                    .catch((error) => {
                                        console.error('Error:', error);
                                    });
                                });
                                pop_pop()
                            } else {
                                let full = document.createElement('p')
                                full.innerHTML = "Class is full";
                                class_box.append(full);
                                let button = document.createElement('button');
                                button.type = "submit";
                                button.className = "waitinglist";
                                button.innerHTML = "Join Waitinglist";
                                button.formAction = "join";
                                let action = "join"
                                class_box.append(button);

                                let favorites = document.createElement('button');
                                favorites.type = "submit";
                                favorites.className = "favorites";
                                fetch(`/in_favorites/${classId}`, {
                                    method: 'GET',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    }
                                })
                                .then(response => response.json())
                                .then(data => {
                                    if (data.fav_status === "add") {
                                        button_text = "Add to favorites"
                                        favorites.innerHTML = `${button_text}`;

                                    }
                                    else if (data.fav_status === "remove") {
                                        button_text = "Remove from favorites"
                                        favorites.innerHTML = `${button_text}`;
                                    }
                                })
                                .catch((error) => {
                                    console.error('Error:', error);
                                });
                                class_box.append(favorites);


                                favorites.addEventListener('click', function(event) {
                                    event.stopPropagation();
                                    favor(classId)
                                })

                                button.addEventListener('click', function(event) {
                                    event.stopPropagation();
                                    fetch(`/waitinglist/${classId}/${action}`, {
                                        method: 'POST',
                                        headers: {
                                            'Content-Type': 'application/json',
                                            'X-CSRFToken': getCookie('csrftoken')
                                        },
                                        body: JSON.stringify({
                                            className: class_info.title
                                        })
                                    })
                                    .then(response => response.json())
                                    .then(data => {
                                        if (data.status === "on_waitlist") {
                                            // if user is on the waiting list
                                            alert('You are already on the waitinglist');
                                            location.reload(); //refreshes the page
                                        } else {
                                        alert('You joined the waitinglist');
                                        location.reload(); //refreshes the page
                                        }
                                    })
                                    .catch((error) => {
                                        console.error('Error:', error);
                                    });
                                });
                                pop_pop()
                            }
                        })
                        .catch((error) => {
                            console.error('Error:', error);
                        });
                    }
                    else {
                        let booked = document.createElement('p')
                        booked.innerHTML = "Booked in";
                        class_box.append(booked);
                        console.log(`You're booked in`);
                        let br = document.createElement('br')
                        class_box.append(br)
                        let button = document.createElement('button');
                        button.type = "submit";
                        button.className = "cancel";
                        button.innerHTML = "Cancel";
                        button.formAction = "cancel";
                        class_box.append(button);

                        class_box.append(br)
                        let favorites = document.createElement('button');
                        favorites.type = "submit";
                        favorites.className = "favorites";
                        fetch(`/in_favorites/${classId}`, {
                            method: 'GET',
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.fav_status === "add") {
                                button_text = "Add to favorites"
                                favorites.innerHTML = `${button_text}`;

                            }
                            else if (data.fav_status === "remove") {
                                button_text = "Remove from favorites"
                                favorites.innerHTML = `${button_text}`;
                            }
                        })
                        .catch((error) => {
                            console.error('Error:', error);
                        });
                        favorites.formAction = "favorite";
                        class_box.append(favorites);

                        favorites.addEventListener('click', function(event) {
                            event.stopPropagation();
                            favor(classId)
                        })

                        button.addEventListener('click', function(event) {
                            event.stopPropagation();
                            fetch(`/cancel/${classId}`, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': getCookie('csrftoken')
                                },
                                body: JSON.stringify({
                                    className: class_info.title
                                })
                            })
                            .then(response => response.json())
                            .then(data => {
                                alert('You cancelled your booking');
                                location.reload(); //refreshes the page
                            })
                            .catch((error) => {
                                console.error('Error:', error);
                            });
                        });
                        pop_pop()
                    }
                }
            }
        });
    });
}

function pop_pop() {
    document.querySelectorAll('.class_box').forEach(slot => {
        slot.addEventListener('click', function(event) {
            let teacher = document.querySelector('.teacher')
            if (teacher) {
                //console.log(document.querySelector('.class_box').getAttribute('data-flag'))
                if (document.querySelector('.class_box').getAttribute('data-flag') === "false" && !event.target.matches('button') && !event.target.matches('select')) {
                    event.target.style.display = 'none';
                    event.stopPropagation();
                    let classBox = event.target.closest('.class_box');
                    if (classBox) {
                        classBox.remove();
                    }
                }
            }
            else {
                event.target.style.display = 'none';
                event.stopPropagation();
                let classBox = event.target.closest('.class_box');
                if (classBox) {
                    classBox.remove();
                }
            }
        });
    });
}

function favor(classId) {
    console.log("click")
    fetch(`/in_favorites/${classId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.fav_status === "add") {
            alert('Class Added to your favorites list');
            action = "add"
        }
        else if (data.fav_status === "remove") {
            alert('Class Removed from your favorites list')
            action = "remove"
        }

        fetch(`/fav/${classId}/${action}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
        })
        .then(response => response.json())
        .then(data => {
            location.reload(); //refreshes the page
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// Booking page

function booking_form_clubs(data) {
    fetch('/get_clubs', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {

        let clubDropdown = document.querySelector('#clubs');
        for (let club of data) {
            let option = document.createElement('option');
            option.value = club.id;
            option.text = club.name;
            clubDropdown.appendChild(option);
        }
    });
}

function booking_form_classes() {
    let clubDropdown = document.querySelector('#clubs');
    clubDropdown.addEventListener('change', function() {
        let select_club = clubDropdown.value;
        fetch(`/get_classes/${select_club}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            // clear previous options
            let classDropdown = document.querySelector('#classes');
            class_dropdown()


            let daysDropdown = document.querySelector('#days');
            day_dropdown()

            let timesDropdown = document.querySelector('#times');
            time_dropdown()

            let uniqueClasses = new Set();
            data.forEach(fit_class => {
                if (!uniqueClasses.has(fit_class.name__title)) {
                    uniqueClasses.add(fit_class.name__title);
                    let option = document.createElement('option');
                    option.value = fit_class.name_id;
                    console.log(`Booking_form_classess: Option Value ${option.value}`)
                    option.text = fit_class.name__title;
                    classDropdown.appendChild(option);
                }
            });
        });
    });
}

function booking_form_days() {
    let clubDropdown = document.querySelector('#clubs');
    let classDropdown = document.querySelector('#classes');
    classDropdown.addEventListener('change', function() {
        let select_club = clubDropdown.value;
        let select_class = classDropdown.value;

        fetch(`/get_days/${select_club}/${select_class}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            // clear previous options
            let daysDropdown = document.querySelector('#days');
            daysDropdown.innerHTML = 'Select a Day';

            let uniqueDays = new Set();
            data.forEach(day => {
                if (!uniqueDays.has(day.day__day)) {
                    uniqueDays.add(day.day__day);
                }
            });
            let daysOrder = ["Monday", "Tuesday", "Wednsday", "Thursday", "Friday", "Saturday", "Sunday"];
            let sortedDays = Array.from(uniqueDays).sort((a, b) => {
                return daysOrder.indexOf(a) - daysOrder.indexOf(b);
            });

            let headerOption = document.createElement('option');
            day_dropdown()

            let timesDropdown = document.getElementById('times');
            time_dropdown()

            sortedDays.forEach(day => {
                let option = document.createElement('option');
                option.value = day; // Adjust this if needed
                option.text = day;
                daysDropdown.appendChild(option);
            });
        });
    });
}

function booking_form_times() {
    let clubDropdown = document.querySelector('#clubs');
    let classDropdown = document.querySelector('#classes');
    let dayDropdown = document.querySelector('#days');
    dayDropdown.addEventListener('change', function() {
        let select_club = clubDropdown.value;
        let select_class = classDropdown.value;
        let select_day = dayDropdown.value;

        fetch(`/get_time/${select_club}/${select_class}/${select_day}`)
        .then(response => response.json())
        .then(data => {
            let timesDropdown = document.getElementById('times');
            time_dropdown();

            data.forEach(time => {
                console.log(`${time}`)
                let option = document.createElement('option');
                option.value = time.slot__id;
                option.text = time.slot__time;
                console.log(`${time.slot__id}`)
                timesDropdown.appendChild(option);
            });
        });
    });
}

function class_dropdown(){
    let classDropdown = document.querySelector('#classes');
    classDropdown.innerHTML = 'Select Classs';

    let headerOption = document.createElement('option');
    headerOption.text = "Select a class";
    headerOption.disabled = true;
    headerOption.selected = true;
    classDropdown.appendChild(headerOption);
}

function day_dropdown() {
    let daysDropdown = document.querySelector('#days');
    daysDropdown.innerHTML = 'Select a Day';
    let headerOptionDays = document.createElement('option');
    headerOptionDays.text = "Select a day";
    headerOptionDays.disabled = true;
    headerOptionDays.selected = true;
    daysDropdown.appendChild(headerOptionDays);
}

function time_dropdown() {
    let timesDropdown = document.querySelector('#times');
    timesDropdown.innerHTML = 'Select the Time';
    let headerOptionTimes = document.createElement('option');
    headerOptionTimes.text = "Select the time";
    headerOptionTimes.disabled = true;
    headerOptionTimes.selected = true;
    timesDropdown.appendChild(headerOptionTimes);
}

function booking_listeners() {
    booking_form_clubs();
    booking_form_classes()
    booking_form_days()
    booking_form_times()
}

// Profile page

function profile(Bookings, Favorites, History) {
    let profilebox = document.querySelector('.profile')
    if (profilebox) {
        let bookingsBox = document.createElement('div');
        bookingsBox.innerHTML = "Bookings:"
        bookingsBox.className = "Bookings"
        profilebox.append(bookingsBox);

        let br = document.createElement('br')
        bookingsBox.append(br)

        let upcomingButton = document.createElement('button');
        upcomingButton,className = "upcoming"
        upcomingButton.innerHTML = "Upcoming"
        bookingsBox.append(upcomingButton)
        upcomingButton.addEventListener('click', function(event) {
            let table = document.getElementById('bookings_table');
            if (table) {
                historyButton.className = "history"
                upcomingButton.className = "upcoming"
                favorites.className = "favorites"
                table.remove();
            } else {
                // Create the table
                let bb = document.querySelector('.Bookings')
                let table_div = document.createElement('div')
                table_div.id = "bookings_table";
                bb.append(table_div)

                let title = document.createElement('p')
                title.className = 'centered';
                title.innerHTML = "Upcoming bookings";
                table_div.append(title)
                upcomingButton.className = "selected"
                let type = "bookings"
                profile_tables(Bookings, type)
            }
        });

        let historyButton = document.createElement('button');
        historyButton.innerHTML = "History"
        bookingsBox.append(historyButton)
        historyButton.addEventListener('click', function(event) {
            let table = document.getElementById('bookings_table');
            if (table) {
                historyButton.className = "history"
                upcomingButton.className = "upcoming"
                favorites.className = "favorites"

                table.remove();
            } else {
                // Create the table
                let bb = document.querySelector('.Bookings')
                let table_div = document.createElement('div')
                table_div.id = "bookings_table";
                bb.append(table_div)

                let title = document.createElement('p')
                title.className = 'centered';
                title.innerHTML = "Past bookings";
                table_div.append(title)
                historyButton.className = "selected"
                let type = "history"
                profile_tables(History, type)

            }
        });

        let favoritesBox = document.createElement('div');
        profilebox.append(favoritesBox)
        let favorites = document.createElement('button');
        favorites.innerHTML = "Favorites"
        bookingsBox.append(favorites)
        favorites.addEventListener('click', function(event) {
            let table = document.getElementById('bookings_table');
            if (table) {
                historyButton.className = "history"
                upcomingButton.className = "upcoming"
                favorites.className = "favorites"
                table.remove();
            } else {
                let bb = document.querySelector('.Bookings')
                let table_div = document.createElement('div')
                table_div.id = "bookings_table";
                bb.append(table_div)

                let title = document.createElement('p')
                title.className = 'centered';
                title.innerHTML = "Favorites";
                table_div.append(title)
                favorites.className = "selected"
                let type = "favorites"
                profile_tables(Favorites, type)
            }
        });
    }
}

function profile_tables(details, type) {
    let table_div = document.getElementById('bookings_table');

    let table = document.createElement('table')
    table_div.append(table)

    let tr = document.createElement('tr')
    table.append(tr)

    const headers = ["Club", "Class", "Day", "Time"]
    let i=0;
    while (i<headers.length){
        let th = document.createElement('th');
        th.innerHTML = `${headers[i]}`;
        tr.append(th)
        i++
    }

    details.forEach(booking => {
        let list = []
        console.log(type)
        if (type === "bookings") {
            list = [`${booking.class_name__club__name}`, `${booking.class_name__name__title}`, `${booking.class_name__day__day}: ${booking.class_name__day__date_today}`, `${booking.class_name__slot__time}`]
        } else if (type === "favorites") {
            list = [`${booking.class_name__club__name}`, `${booking.class_name__name__title}`, `${booking.class_name__day__day}`, `${booking.class_name__slot__time}`]
        } else {
            list = [`${booking.club}`, `${booking.fit_class}`, `${booking.day}`, `${booking.time}`]
        }
        let tr = document.createElement('tr')
        table.append(tr)
        let j = 0;

        while (j < list.length) {
            let td = document.createElement('td');
            td.innerHTML = `${list[j]}`;
            tr.append(td)
            j++
        }
    });
}

// Teachers Page

function teachers(clubsData, daysData, timesData, classesData, usersData, userInfo, description) {
    let TB = document.querySelector('.teacher');

    let new_class_form = document.getElementById('newClass');

    TB.setAttribute('data-user_id', userInfo.id);

    // Create a new class
    let j = 0
    let list2 = ["Class Title", "Description", "Capacity", "Active", "Teacher"];
    while (j < list2.length) {
        let label = document.createElement('label');
        label.htmlFor = `${list2[j]}`;
        label.innerHTML = `${list2[j]}:`;
        new_class_form.append(label);
        if (list2[j] === "Class Title") {
            let input = document.createElement('input');
            input.type = "text";
            input.id = "class_title";
            input.name = "class_title";
            input.pattern = "[A-Za-z0-9 ]*";
            input.title = "Only letters, numbers, and spaces are allowed";
            new_class_form.append(input);
        } else if (list2[j] === "Description") {
            let input = document.createElement('input');
            input.type = "text";
            input.id = "description";
            input.name = "description";
            input.pattern = "[A-Za-z0-9 ]*";
            input.title = "Only letters, numbers, and spaces are allowed";
            new_class_form.append(input);
        } else if (list2[j] === "Capacity") {
            let input = document.createElement('input');
            input.type = "number";
            input.id = "capacity";
            input.name = "capacity";
            new_class_form.append(input);
        } else if (list2[j] === "Active") {
            let input = document.createElement('input');
            input.type = "radio";
            input.id = "active";
            input.name = "active";
            new_class_form.append(input);
        }

        if (list2[j] === "Teacher") {
            let select = document.createElement('select');
            select.id = "users";
            select.name = "users";
            new_class_form.append(select);
            let choice2 = document.createElement('option');
            choice2.text = "Selec a teacher";
            select.append(choice2);

            if (userInfo.username === "admin") {
                for (let user of usersData) {
                    let choice = document.createElement('option');
                    choice.value = user.id;
                    choice.text = user.username;
                    select.append(choice);
                }
            } else {
                let choice = document.createElement('option');
                choice.value = userInfo.id;
                choice.text = userInfo.username;
                select.append(choice);
            }
        }
        j++
    }
    newClass()
    let button2 = document.createElement('button');
    button2.type = "submit";
    button2.innerHTML = "Create Class";
    new_class_form.append(button2);

    let class_form = document.getElementById('classForm');

    //Book class
    let admin = document.getElementById('admin');
    if (admin) {
        let list = ["Club", "Day", "Time", "Class", "Capacity"];
        let i = 0;

        while (i < list.length) {
            let label = document.createElement('label');
            label.htmlFor = `${list[i]}`;
            label.innerHTML = `${list[i]}:`;
            class_form.append(label);

            let br = document.createElement('br');

            if (list[i] === "Club") {
                let select = document.createElement('select');
                select.id = "club";
                select.name = "club";
                class_form.append(select);
                let choice = document.createElement('option');
                choice.text = "Selec a club";
                select.append(choice);


                for (let club of clubsData) {
                    let choice = document.createElement('option');
                    choice.value = club.id;
                    choice.text = club.name;
                    select.append(choice);
                }
            } else if (list[i] === "Day") {
                let select = document.createElement('select');
                select.id = "day";
                select.name = "day";
                class_form.append(select);
                let choice = document.createElement('option');
                choice.text = "Selec a day";
                select.append(choice);

                for (let day of daysData) {
                    let choice = document.createElement('option');
                    choice.value = day.id;
                    choice.text = day.day;
                    select.append(choice);
                }
            } else if (list[i] === "Time") {
                let select = document.createElement('select');
                select.id = "time";
                select.name = "time";
                class_form.append(select);
                let choice = document.createElement('option');
                choice.text = "Selec a time";
                select.append(choice);

                for (let time of timesData) {
                    let choice = document.createElement('option');
                    choice.value = time.id;
                    choice.text = time.time;
                    select.append(choice);
                }

            } else if ( list[i] === "Class") {
                let select = document.createElement('select');
                select.id = "Class";
                select.name = "Class";
                class_form.append(select);
                let choice = document.createElement('option');
                choice.text = "Selec a class";
                select.append(choice);

                for (let clas of classesData) {
                    let choice = document.createElement('option');
                    choice.value = clas.id;
                    choice.text = clas.title;
                    select.append(choice);
                }
            }
            i++;
        }
        class_check()
        let button = document.createElement('button');
        button.type = "submit";
        button.innerHTML = "Book a Class";
        class_form.append(button);
    }

}


function class_check() {
    document.getElementById('classForm').addEventListener('submit', function(event) {
        event.preventDefault(); // prevent the default form submission

        let club = document.getElementById('club').value;
        let day = document.getElementById('day').value;
        let time = document.getElementById('time').value;
        let classId = document.getElementById('Class').value;

        fetch('/teacher_class/book', {
            method: 'POST',
            body: JSON.stringify({ club: club, day: day, time: time, class: classId, overwrite: false }),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Class exists') {
                if (confirm("Slot is already taken. Overwrite?")) {
                    fetch('/teacher_class/book', {
                        method: 'POST',
                        body: JSON.stringify({ club: club, day: day, time: time, class: classId, overwrite: true }),
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        alert("Class overwritten successfully");
                        location.reload()
                    })
                    .catch(error => {
                        alert("Error: " + error);
                    });
                }
            } else {
                alert("Class booked successfully");
                location.reload()
            }
        })
        .catch(error => {
            alert("Error: " + error);
        });
        return false;
    });
}

function newClass() {
    document.getElementById('newClass').addEventListener('submit', (event) => {
        event.preventDefault();
        let formData = new FormData(event.target);
        let jsonData = {};
        formData.forEach((value, key) => {
            jsonData[key] = value;
        });

        fetch('/teacher_class/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            },
            body: JSON.stringify(jsonData)
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);

            if (data.message === 'Exists') {
                alert("Class already exists");
                location.reload()
            }
            else {
                alert("Class created successfully");
                location.reload()
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
}

function teacher_view_listener (classes, timetables) {
    document.querySelectorAll('.class_slot').forEach(slot => {
        slot.addEventListener('click', function(event) {
            let classBox = document.querySelector('.class_box');
            if (classBox) {
                classBox.remove();
            }
            let classId = event.target.getAttribute('data-id');
            let classCap = event.target.getAttribute('data-capcity'); //capacity for this class
            let is_booked = event.target.getAttribute('data-is-booked');
            document.querySelectorAll('.class_box').forEach(popup => {
                popup.style.display = 'none';
            });

            let className = event.target.innerHTML;

            let slotId = event.target.id;

            // display popout with details for the clicked slot
            const class_slot = document.querySelector(`#${slotId}`);

            // get the class information based on its name
            let class_info = classes.find(t => t.title === className)

            // Creates a popout slot in the timetable when clicked! change POPOUT POSITIONING BY ADJUSTING THE PIXELS

            const class_box = document.createElement('div');
            class_box.className = "class_box";
            class_box.id = `${slotId}`
            //Alternative to styles way to set the position
            //class_box.style.top = `${event.target.offsetTop + 50}px`;
            //class_box.style.left = `${event.target.offsetLeft + event.target.offsetWidth + 180}px`;
            let br = document.createElement('br')
            document.body.append(class_box);

            if (class_info) {
                class_time_check(classId)
                console.log(`test test ${classId}`)
                class_box.innerHTML = `${class_info.description}.<br><br> People booked in: ${classCap}.`;

                class_box.append(br)
                class_box.setAttribute('data-flag', 'false');

                let deleteButton = document.createElement('button');
                deleteButton.type = "submit";
                deleteButton.className = "manage";
                fetch(`/teacher_check/${classId}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    // Button text based on teacher response
                    if (data.teacher === "True") {
                        button_text = "Delete"
                        deleteButton.innerHTML = `${button_text}`;
                        action = "Delete"
                        class_box.append(deleteButton)
                    }
                    else if (data.teacher === "False") {
                        action = "Nothing"
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                });

                deleteButton.addEventListener('click', function(event) {
                    event.stopPropagation();
                    fetch(`/teacher_delete/${classId}/${action}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        // Handle the response data
                        location.reload(); //refreshes the page
                    })
                    .catch((error) => {
                        console.error('Error:', error);
                    });
                })

                pop_pop()
            }
            //If blank class slot
            else {
                let classDay = event.target.getAttribute('data-day')
                let classTime = event.target.getAttribute('data-time')

                let freeText = document.createElement('p');
                freeText.innerHTML = "Free booking slot";
                class_box.append(freeText)
                let freeBook = document.createElement('button');
                freeBook.type = "submit";
                freeBook.className = "booking";
                freeBook.innerHTML = "Book";
                freeBook.formAction = "book";

                class_box.setAttribute('data-flag', 'false');
                class_box.append(freeBook);

                slot_book(classDay, classTime)

                pop_pop()
            }
        });
    });
}


// slot booking functino
function slot_book(classDay, classTime) {
    document.querySelectorAll('.booking').forEach(slot => {
        slot.addEventListener('click', function(event) {


            let class_box = event.target.closest('.class_box');
            let flag = class_box.getAttribute('data-flag')

            class_box.innerHTML = "";
            let teacher_box = document.querySelector('.teacher');

            const classesData = JSON.parse(teacher_box.dataset.classes);

            let form = document.createElement("form");
            form.setAttribute("id", "newClass");
            form.setAttribute("method", "POST");
            form.setAttribute("action", "/teacher_class/create");
            class_box.append(form);

            let csrfToken = document.createElement("input");
            csrfToken.setAttribute("type", "hidden");
            csrfToken.setAttribute("name", "csrfmiddlewaretoken");
            csrfToken.setAttribute("value", getCookie('csrftoken'));
            form.appendChild(csrfToken);

            let class_form = document.getElementById('classForm');
            let list = ["Club", "Day", "Time", "Class"];
            let i = 0;

            while (i < list.length) {
                let label = document.createElement('label');
                label.htmlFor = `${list[i]}`;
                label.innerHTML = `${list[i]}:`;
                form.append(label);

                let br = document.createElement('br');

                if (list[i] === "Club") {
                    let select = document.createElement('select');
                    select.id = "club";
                    select.name = "club";
                    form.append(select);

                    const bodyElement = document.querySelector('.body');
                    const selectedClub = bodyElement.dataset.club_selected;
                    const clubsData = JSON.parse(teacher_box.dataset.clubs);
                    const clubId = clubsData.find(club => club.name === selectedClub).id;

                    let choice = document.createElement('option');
                    choice.value = clubId;
                    choice.text = selectedClub;
                    select.append(choice);

                } else if (list[i] === "Day") {
                    let select = document.createElement('select');
                    select.id = "day";
                    select.name = "day";
                    form.append(select);

                    const daysData = JSON.parse(teacher_box.dataset.days);
                    const dayId = daysData.find(day => day.day === classDay).id;

                    let choice = document.createElement('option');
                    choice.value = dayId;
                    choice.text = classDay;
                    select.append(choice);

                } else if (list[i] === "Time") {
                    let select = document.createElement('select');
                    select.id = "time";
                    select.name = "time";
                    form.append(select);

                    const timesData = JSON.parse(teacher_box.dataset.times);
                    const timeId = timesData.find(time => time.time === classTime).id;

                    let choice = document.createElement('option');
                    choice.value = timeId;
                    choice.text = classTime;
                    select.append(choice);

                } else if ( list[i] === "Class") {
                    let select = document.createElement('select');
                    select.id = "Class2";
                    select.name = "Class2";
                    form.append(select);

                    let TB = document.querySelector('.teacher');
                    let user_id = TB.getAttribute('data-user_id');
                    const teacherClasses = classesData.filter(clas => clas.teacher_id == user_id);
                    let choice = document.createElement('option');
                    choice.text = "Selec a class";
                    select.append(choice);

                    if (user_id != "4") {
                        for (let clas of teacherClasses) {
                            let choice2 = document.createElement('option');
                            choice2.value = clas.id;
                            choice2.text = clas.title;
                            select.append(choice2);
                        }
                    }
                    else{
                        for (let clas of classesData) {
                            let choice = document.createElement('option');
                            choice.value = clas.id;
                            choice.text = clas.title;
                            select.append(choice);
                        }
                    }
                }
                i++;
            }
            console.log("Adding button")

            let button = document.createElement('button');
            button.id = "book-button";
            button.type = "submit";
            button.innerHTML = "Book a Class";
            form.append(button);

            //Converts the form data into JSON
            form.addEventListener('submit', function(event) {
                event.preventDefault(); // Prevent the default form submission

                let formData = new FormData(form);
                let jsonData = {};

                formData.forEach((value, key) => {
                    jsonData[key] = value;
                });

                fetch('/teacher_class/book', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(jsonData)
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    location.reload()
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });
        });
    });
}

function notification_check() {
    fetch(`/notification_check`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Button text based on teacher response
        if (data.notice === "NOTFICATION") {
            alert("You have a new notification(s)")
            let notice = document.querySelector("#notice");
            notice.dataset.flag = true
            notice.innerHTML = "*New Notification*!"
            notice.style.background = "red";
            notice.style.fontWeight = "bold";
        }
        else {
            console.log("No notifications")
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function notif_board() {
    const element = document.querySelector('#notice');
    if (element) {
        element.addEventListener("click", function(event) {
            fetch("/notif_board")
            .then(response => {
                return response.json();
            })
            .then(data => {
                //CREATE POPUP
                const notif_box = document.createElement('div');
                notif_box.id = "notif_box";

                const table = document.createElement('table');
                notif_box.append(table);

                let tr = document.createElement('tr');
                table.append(tr);

                let th = document.createElement('th');
                th.innerHTML = "Notification";
                tr.append(th)

                th = document.createElement('th');
                th.innerHTML = "Book";
                tr.append(th)

                if (data.flag === true) {
                    let notifList = data.notif_list;

                    let length = notifList.length;
                    let i = 0;
                    while (i < length) {
                        let classId = data.notif_list[i].tt_class.id
                        let class_info = data.notif_list[i].tt_class.name

                        notif_box.style.top = `${event.target.offsetTop + 250}px`;
                        notif_box.style.left = `${event.target.offsetLeft + event.target.offsetWidth - 50}px`;

                        let tr2 = document.createElement('tr'); // creates a row
                        table.append(tr2);

                        let td = document.createElement('td');
                        td.innerHTML = `Booking available for: ${notifList[i].tt_class.name} on ${notifList[i].tt_class.day}@${notifList[i].tt_class.slot} in ${notifList[i].tt_class.club}`;
                        tr2.append(td)

                        td = document.createElement('td');
                        td.style.textAlign = "center";  // Center horizontally
                        td.style.verticalAlign = "middle";  // Center vertically
                        tr2.append(td);

                        let buttonB = document.createElement('button');
                        buttonB.type = "submit";
                        buttonB.className = "booking";
                        buttonB.innerHTML = "Book";
                        buttonB.formAction = "book";
                        td.append(buttonB);

                        i++

                        buttonB.addEventListener('click', function(event) {
                            event.stopPropagation();
                            let action = "exit";

                            fetch(`/book/${classId}/${action}`, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': getCookie('csrftoken')
                                },
                                body: JSON.stringify({
                                    className: class_info
                                })
                            })
                            .then(response => response.json())
                            .then(data => {
                                alert('You are booked in');

                                location.reload();

                            })
                            .catch((error) => {
                                console.error('Error:', error);
                            });
                        });
                    }
                }
                else if (data.flag === false) {
                    notif_box.style.top = `${event.target.offsetTop + 250}px`;
                    notif_box.style.left = `${event.target.offsetLeft + event.target.offsetWidth + 150}px`;
                    notif_box.innerHTML = "No notifications";
                    notif_box.style.width = "400px";
                    notif_box.style.height = "200px";
                    notif_box.style.textAlign = "center";
                    notif_box.style.lineHeight = "100px";
                    notif_box.style.fontSize = "26px";
                }
                else {
                    console.log(`Error. Flag: ${data.flag}`)
                }
                document.body.append(notif_box);

                let notice = document.querySelector("#notice");
                notice.dataset.flag = "false";
                console.log(` dataFlag: ${notice.dataset.flag}`)

                document.querySelectorAll('#notif_box').forEach(slot => {
                    slot.addEventListener('click', function(event) {
                        event.stopPropagation();
                        let notifBox = event.target.closest('#notif_box');
                        if (notifBox && !event.target.matches('button') && !event.target.matches('td')) {
                            event.target.style.display = 'none';
                            notifBox.remove();
                            location.reload();
                        }
                    });
                });
            });
        });
    }
}

function checkClass() {
    const now = new Date();
    const currentDay = now.getDay(); // 0 = Sunday, 1 = Monday, ..., 6 = Saturday
    const currentTime = now.toISOString().split('.')[0];
    const tt_class = getClass(currentTime)
}

function getClass(time) {
    fetch(`/class_time_check/${time}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Handle the response data
        if (data.class.length > 0) {
            // Class found, handles the logic here
            console.log("Class found:", data.class);
        } else {
            console.log("No class found at this time.");
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function startCheckClassOnHour() {
    const now = new Date();
    const minutesUntilNextHour = 59 - now.getMinutes();
    const secondsUntilNextHour = 59 - now.getSeconds();
    const millisecondsUntilNextHour = (minutesUntilNextHour * 60 + secondsUntilNextHour) * 1000;

    setTimeout(() => {
        date_update(); // Checks and updates the dates
        placeholder_time_checker(); //Checks if it's less than 12h till class
        setInterval(startCheckClassOnHour, 3600000); // Update the dates every hour
    }, millisecondsUntilNextHour);
}

function date_update() {
    fetch(`/date_update`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Dates updated")
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function placeholder_time_checker() {
    fetch(`/placeholder_time_checker`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Dates updated")
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function class_time_check(class_id) {
    fetch(`/class_time_check/${class_id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function PH_token(class_id) {
    fetch(`/PH_token/${class_id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
