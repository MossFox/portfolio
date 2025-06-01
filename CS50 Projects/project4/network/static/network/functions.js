console.log("JavaScript file loaded");


let like_counter = 0

// Post load function
function load(page = 1, username = null) {
    fetch(`/posts?page=${page}`)
        .then(response => response.json())
        .then(data => {
            document.querySelector('#posts').innerHTML = ''; // Clear previous posts
            data.posts.forEach(post => {
                add_post(post, data.liked_posts);
            });
            addLikeEventListeners();
            editEventListener(); // Call editEventListener after posts are loaded

            // Add pagination controls
            if (data.has_previous) {
                document.querySelector('#previous').style.display = 'block';
                document.querySelector('#previous').onclick = () => load(page - 1);
            } else {
                document.querySelector('#previous').style.display = 'none';
            }

            if (data.has_next) {
                document.querySelector('#next').style.display = 'block';
                document.querySelector('#next').onclick = () => load(page + 1);
            } else {
                document.querySelector('#next').style.display = 'none';
            }
        });
}

//Add new posts
function add_post(post, liked_posts) {
    const postID = post.id
    const loggedInUserId = document.getElementById('user-info').getAttribute('data-user-id');
    const post_box = document.createElement('div');
    post_box.style = 'border: 0.5px solid; padding: 20px; margin-top: 20px'
    post_box.className = 'post_box';
    post_box.id = postID;
    if (document.querySelector('#posts')) {
        document.querySelector('#posts').append(post_box);
    } else if (document.querySelector('#profile_posts')) {
        document.querySelector('#profile_posts').append(post_box);
    } else if (document.querySelector('#following_posts')) {
        document.querySelector('#following_posts').append(post_box);
    } else {
        console.warn("No valid container for posts found.");
    }

    const anchor = document.createElement('a');
    anchor.className = 'postTitle';
    anchor.innerHTML = `${post.title}`;
    post_box.append(anchor);

    const breakk = document.createElement('br');
    post_box.append(breakk)

    const postContent = document.createElement('div');
    postContent.className ='postContent';
    postContent.innerHTML = post.post;
    post_box.append(postContent);

    const like_img = document.createElement('a');
    like_img.className = "like_button";
    like_img.dataset.postId = post.id;
    like_img.innerHTML = `<img src="/static/like.png" style = "margin-left:-10px; height:40px; width:40px" alt="Like">`
    post_box.append(like_img);

    const like = document.createElement('a');
    like.className = 'like_count';
    like.innerHTML = `${post.like} <br>`;
    post_box.append(like);

    const posted_by = document.createElement('a');
    posted_by.className = "posted_by";
    posted_by.innerHTML = `Posted by: <a href="/profile/${post.user}">${post.user}</a> on ${post.date_time}`;
    post_box.append(posted_by);
    post_box.append(breakk);


    if (parseInt(loggedInUserId) === parseInt(post.user_id)) {
        const editLink = document.createElement('a');
        editLink.href = `/post_edit/${post.id}`;
        editLink.className = "edit_button";
        editLink.innerHTML = 'Edit';
        post_box.append(editLink);
    }

}

function profile_load(user) {
    // get the logged in user id from the html data box
    const loggedInUserId = document.getElementById('user-info').getAttribute('data-user-id');
    //
    const isFollowing = user.is_following;
    const profileBox = document.createElement('div');
    profileBox.id = "profile_box";
    document.querySelector('#profile').append(profileBox);

    const user_name = document.createElement('h3');
    user_name.innerHTML = `User: ${user.name}`;
    profileBox.append(user_name);

    const followers = document.createElement('div');
    followers.id = "followers";
    followers.innerHTML = `User has ${user.followers} followers`;
    profileBox.append(followers);

    const following = document.createElement('div');
    following.id = "following";
    following.innerHTML = `User follows ${user.following} people`;
    profileBox.append(following);

    if (parseInt(loggedInUserId) != parseInt(user.id)) {
        const follow_unfollow = document.createElement('button');
        follow_unfollow.className = "follow_unfollow";
        follow_unfollow.innerHTML = isFollowing ? 'Unfollow' : 'Follow';
        profileBox.append(follow_unfollow);
        follow_unfollow.addEventListener('click', () => follow_toggle(user.name));
    }

    // Load posts from initial data in data-posts
    const postsData = JSON.parse(document.getElementById('user-info').getAttribute('data-posts'));
    displayPosts(postsData);
}

function displayPosts(posts) {
    posts.forEach(post => {
        add_post(post);
    });
    addLikeEventListeners();
    editEventListener();
}

function follow_toggle (username) {
    fetch(`/profile/${username}/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (response.ok) {
            const followButton = document.querySelector('.follow_unfollow');
            const followersCount = document.getElementById('followers');
            //selects the inner html of followers count, .match(/\d+/)  uses a
            //regular expression to find one or more digits in the string. \d+ matches one or
            //more digits. The match method returns an array of matches.
            // [0] accesses the first match in the array, which is the number of followers as a string.
            // parseInt(...)  converts the string representation of the number to an integer
            let currentCount = parseInt(followersCount.innerHTML.match(/\d+/)[0]);

            if (followButton.innerHTML === 'Follow') {
                followButton.innerHTML = 'Unfollow';
                currentCount += 1;
            } else {
                followButton.innerHTML = 'Follow';
                currentCount -= 1;
            }

            followersCount.innerHTML = `User has ${currentCount} followers`;
        } else {
            console.log('Error');
        }
    });
}

function addLikeEventListeners() {
    document.querySelectorAll('.like_button').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            const button = event.target.closest('.like_button');
            const postId = button.dataset.postId;

            fetch(`/like/${postId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                updateLikeUI(button, data);
            })
            .catch(error => console.error('Error:', error));
        });
    });
}

function editEventListener () {
    document.querySelectorAll('.edit_button').forEach(button => {
        if (!button.dataset.listenerAttached) {
            button.dataset.listenerAttached = true;

            button.addEventListener('click', (event) => {
                button.style.display = 'none';
                event.preventDefault();

                const postBox = event.target.closest('.post_box');
                const postID = postBox.id;

                const postTitle = postBox.querySelector('.postTitle');
                const originalTitle = postTitle.innerHTML;

                const titleInput = document.createElement('textarea');
                titleInput.value = originalTitle;
                titleInput.name = "title"

                postTitle.innerHTML = '';

                postTitle.append(titleInput);

                const postContent = postBox.querySelector('.postContent');
                const originalContent = postContent.innerHTML;

                // Replace post content with a textarea
                const postInput = document.createElement('textarea');
                postInput.value = originalContent;
                postInput.name = "post";
                postContent.innerHTML = '';
                postContent.append(postInput);

                const breakk = document.createElement('br');
                postContent.append(breakk);

                // Add a save button
                const saveButton = document.createElement('button');
                saveButton.innerHTML = 'Save';
                postContent.append(saveButton);

                // Handle save button click
                saveButton.addEventListener('click', () => {
                    const updatedTitle = titleInput.value;
                    const updatedContent = postInput.value;

                    const csrfToken = getCookie('csrftoken');

                    // posting info to the server
                    postTitle.innerHTML = updatedTitle;
                    postContent.innerHTML = updatedContent;
                    fetch(`/post_edit/${postID}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({
                            title: updatedTitle,
                            post: updatedContent
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            postTitle.innerHTML = updatedTitle;
                            postContent.innerHTML = updatedContent;
                        } else {
                            console.error('Error:', data.error);
                        }
                    })
                    .catch(error => console.error('Error:', error));
                    button.style.display = 'inline';
                });
            });
        }
    });
}

function updateLikeUI(button, data) {
    const likeCount = button.nextElementSibling;
    if (data.message === "You liked it.") {
        button.classList.add('liked');
        likeCount.innerHTML = `${parseInt(likeCount.textContent) + 1} <br>`;
    } else if (data.message === "You unliked it.") {
        button.classList.remove('liked');
        likeCount.innerHTML = `${parseInt(likeCount.textContent) - 1}<br>`;
    }
}

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

function loadProfilePosts(page, user) {
    const username = user.name;

    fetch(`/profile/${username}?page=${page}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        document.querySelector('#profile_posts').innerHTML = '';
        data.posts.forEach(post => add_post(post));

        // Update the visibility and onclick handlers for pagination buttons
        document.querySelector('#previous').style.display = data.has_previous ? 'block' : 'none';
        document.querySelector('#next').style.display = data.has_next ? 'block' : 'none';

        if (data.has_previous) {
            document.querySelector('#previous').onclick = () => {
                loadProfilePosts(page - 1, user);
            };
        }

        if (data.has_next) {
            document.querySelector('#next').onclick = () => {
                loadProfilePosts(page + 1, user);
            };
        }
    })
    .catch(error => {
        console.error('Error loading posts:', error);
    });
}

function loadFollowingPosts(page) {
    fetch(`/following?page=${page}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Update posts
        document.querySelector('#following_posts').innerHTML = '';
        data.posts.forEach(post => add_post(post));

        // Handle pagination
        document.querySelector('#previous').style.display = data.has_previous ? 'block' : 'none';
        document.querySelector('#next').style.display = data.has_next ? 'block' : 'none';

        if (data.has_previous) {
            document.querySelector('#previous').onclick = () => {
                loadFollowingPosts(page - 1);
            };
        }

        if (data.has_next) {
            document.querySelector('#next').onclick = () => {
                loadFollowingPosts(page + 1);
            };
        }
    })
    .catch(error => {
        console.error('Error loading posts:', error);
    });
}


