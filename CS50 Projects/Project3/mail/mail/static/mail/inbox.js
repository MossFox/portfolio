document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';


  document.querySelector('#compose-form').onsubmit = () => {
    event.preventDefault();
    const from = document.querySelector('#user_email').value;
    const recipient = document.querySelector('#compose-recipients').value;
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
          from: from,
          recipients: recipient,
          subject: subject,
          body: body
      })
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
          alert(result.error);
        } else {
          alert(result.message);
          // Clear out composition fields
          document.querySelector('#compose-recipients').value = '';
          document.querySelector('#compose-subject').value = '';
          document.querySelector('#compose-body').value = '';

          load_mailbox('sent');

        }
    });
  };
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  document.querySelector('#emails-view').innerHTML = '';

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  let mybox = mailbox

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    // Loop through emails
    emails.forEach(email => {
      // Create a new element for each email
      const emailElement = document.createElement('div');
      emailElement.id = `email-${email.id}`;
      emailElement.innerHTML = `<p id="mail"> From: ${email.sender}, Subject: ${email.subject}, Time: ${email.timestamp}</p>`;

      // Append the new element to #emails-view
      document.querySelector('#emails-view').appendChild(emailElement);
      console.log(mailbox)
      if (email.read === true || mybox == "sent") {
        emailElement.style.backgroundColor = 'LightGray';
      } else {
        emailElement.style.backgroundColor = 'white';
      }

      // Mouse over event
      emailElement.addEventListener('mouseover', function() {
        emailElement.style.color = 'blue';
        emailElement.style.cursor = 'pointer';
        emailElement.style.textDecoration = 'underline';
      });
      emailElement.addEventListener('mouseout', function() {
        emailElement.style.color = '';
        emailElement.style.cursor = '';
        emailElement.style.textDecoration = '';
      });

      // Click event
      emailElement.addEventListener('click', () => {
        load_email(email.id, mailbox);
        if (email.read === false) {
          fetch(`/emails/${email.id}`, {
            method: 'PUT',
            body: JSON.stringify({
              read: true
            })
          })
          .then(() => {
            email.read = true;
          });
        }
      });
    });
  });
}

function load_email(email_id, mailbox) {
  // Show the mailbox and hide other views
  document.querySelector('#email-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';

  // Show the mailbox name
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    let subject = document.querySelector('#email_subject').innerHTML = `${email.subject}`;
    let sender = document.querySelector('#email_from').innerHTML = `${email.sender}`;
    let time = document.querySelector('#time').innerHTML = `${email.timestamp}`;
    let recipient = document.querySelector('#email_to').innerHTML = `To: ${email.recipients}`;
    let message = document.querySelector('#email_body').innerHTML = `${email.body.charAt(0).toUpperCase() + email.body.slice(1).replace(/\n/g, '<br>')}`;

    const user_email = document.querySelector('#user_email').value;
    if (mailbox !== 'sent') {
      // Archive
      let archive = document.querySelector(`.archive-button`);
      if (!archive) {
        archive = document.createElement('button');
        archive.className = 'archive-button';
        const br = document.createElement('br');
        document.querySelector('#email-view').appendChild(br);
        document.querySelector('#email-view').appendChild(archive);
      }

      if (email.archived === false) {
        archive.innerText = 'Archive';
      } else {
        archive.innerText = 'Un-Archive';
      }

      // Remove existing event listener
      const newArchive = archive.cloneNode(true);
      archive.replaceWith(newArchive);

      newArchive.addEventListener('click', () => {
        const newStatus = !email.archived; // toggles the archived status, saving the opposite
        fetch(`/emails/${email.id}`, {
          method: 'PUT',
          body: JSON.stringify({
            archived: newStatus //sets the new status
          })
        })
        .then(() => {
          load_mailbox('inbox');
        });
      });
    } else {
      // Hide or remove the archive button if the sender is the current user
      const archive = document.querySelector(`.archive-button`);
      if (archive) {
        archive.remove();
      }
    }

    let reply = document.querySelector(`#reply_button`);
    if (mailbox === 'sent' && reply) {
      reply.remove();
    }
    if (mailbox !== 'sent' && !reply) {
      // Reply
      reply = document.createElement('button');
      reply.id = 'reply_button';
      reply.innerText = 'Reply';
      document.querySelector('#email-view').appendChild(reply);
    };

    if(mailbox !=='sent') {
      document.querySelector('#reply_button').addEventListener('click', () => {
        reply_to_email (email, email.timestamp);
      });
    }
  });
}


function reply_to_email (email, time) {

  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';

  const from = document.querySelector('#user_email').value;
  document.querySelector('#compose-recipients').value = email.sender;
  let old_message = '';
  let subject = email.subject;
  if (subject.startsWith('RE: ')) {
    document.querySelector('#compose-subject').value = subject;
    old_message = email.body
  } else {
    subject = `RE: ${subject}`;
    document.querySelector('#compose-subject').value = subject;
    old_message = `On ${time} ${email.sender} wrote: \n "${email.body}" \n\n`;
  }
  let old_length = old_message.length;
  document.querySelector('#compose-body').value = old_message;

  document.querySelector('#compose-form').onsubmit = () => {
    event.preventDefault();
    const user_input = document.querySelector('#compose-body').value;
    console.log(user_input);
    let time = new Date().toString();
    time = time.slice(0,24);

    const new_message = `${old_message} \n On ${time} ${from} replied:\n "${document.querySelector('#compose-body').value.slice(old_length)}"\n\n`;
    console.log(new_message)

    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
        from: from,
        recipients: email.sender,
        subject: subject,
        body: new_message
      })
    })
    .then(response => response.json())
    .then(result => {
      if (result.error) {
        alert(result.error);
      } else {
        alert(result.message);

        document.querySelector('#compose-recipients').value = '';
        document.querySelector('#compose-subject').value = '';
        document.querySelector('#compose-body').value = '';

        // Load the sent mailbox
        load_mailbox('sent');
      }
    });
  };
}
