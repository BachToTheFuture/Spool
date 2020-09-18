
var type = "login";

function swap(){
	if (type == 'login'){
		type = 'signup';
		$("#switch").html("Already have an account? Sign in here.");
		$("#password2-div").removeClass('hide');
		$("#submit").attr("value", "Sign Up");
		$("#login-text").html("Create a new account");
	}
	else {
		type = 'login';
		$("#switch").html("New to Spool? Sign up here.");
		$("#password2-div").addClass('hide');
		$("#submit").attr("value", "Sign In");
		$("#login-text").html("Sign in");
	}
}

$(document).ready(() => {
    
    // The following makes sure that only one thread gets the hover effect
    // at a time.
    $('.thread').mouseover(function(e) {
        e.stopPropagation();
        $(this).addClass('thread-hovered');
    });
    $('.thread').mouseout(function() {
        $(this).removeClass('thread-hovered');
    });

    
})