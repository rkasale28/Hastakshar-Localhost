function verifyEmail() {
    $('#id_email').attr('readonly', true);

    username = $('#username').val().trim()
    mail = $('#id_email').val().trim()

    var num = ''
    for (i = 0; i < 5; i++) {
        digit = Math.floor(Math.random() * 10);
        num = num + digit.toString()
    }

    var msg = "Dear " + username + ",<br>You have requested for changing your email. <br>Your OTP for HastAkshar Account Email Updation is: " + num + ".<br>Kindly DO NOT share this One-Time-Password with anyone!<br><br>--<br>Warm Regards,<br>Support Team at HastAkshar"
    Email.send({
        Host: "smtp.gmail.com",
        Username: "hastakshar.noreply@gmail.com",
        Password: "Password_1",
        To: mail,
        From: "hastakshar.noreply@gmail.com",
        Subject: "[IMPORTANT] OTP for HastAkshar Account Email Updation",
        Body: msg
    }).then(function (message) {
        alert("OTP sent successfully to registered email address!")

        $("#otp1_1").val(num)
        $('#otp_button').css("display", "none");
        $('#div_id_otp_1').css("display", "block");
        $('#submit_1').css("display", "block");
    });
}

$("#id_email").keyup(function () {
    var email = $(this).val().trim();
    var username = $("#username").val().trim();
    var bool;

    $.ajax({
        url: '../ajax/validate_reset_email/',
        data: {
            'username': username,
            'email': email
        },
        dataType: 'json',
        success: function (data) {
            display("#email-error-1", email == "")
            display("#email-error-2", data.invalid)
            display("#email-error-3", data.same)

            bool = email == "" || data.invalid || data.same
            enable("#otp_button", bool)
        }
    });
});

$("#otp2_1").keyup(function () {
    var otp1 = $("#otp1_1").val().trim()
    var otp2 = $(this).val().trim();
    
    display("#otp-1-error-1",otp2 == "")
    display("#otp-1-error-2",(otp2 != "" && otp1!=otp2))
    enable("#submit_1", (otp2 == "" || otp1!=otp2))
});
