function validateEmail(email) {
    /*var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;*/
    var re = /^(([^<>()\[\]\.,;:\s@\"]+(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;
    return re.test(email);
}

function validateUrl(userInput) {
    var res = userInput.match(/(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g);
    if(res == null)
        return false;
    else
        return true;
}

$(document).ready(function(){


	$('#nickname__save-button').removeAttr('disabled');


	$('#nickname__edit-input').on('keyup', function(e){
		if (e.which!=13){
			if ($(this).val().length<30) {
				getResults('/check-nick','json',{val: $(this).val()}, function(res){
					if (res.val == 1){
						$('#nickname__group').removeClass('has-success');
						$('#nickname__group').addClass('has-error');
						$('#nickname__save-button').attr('disabled','disabled');
						$('#nickname__status').html('<span style="color:red">Это имя уже занято</span>');
					} else if (res.val==0){
						$('#nickname__group').removeClass('has-error');
						$('#nickname__group').addClass('has-success');
						$('#nickname__save-button').removeAttr('disabled');
						$('#nickname__status').html('<span style="color:green">Это имя свободно!</span>');
					}
					$('#nickname__status').show();

				});
			}
			else{
				$('#nickname__status').html('<span style="color:red">Это имя слишком длинное</span>');
				$('#nickname__save-button').attr('disabled','disabled');
			}
		} else {
			$('#nickname__save-button').trigger('click');
		}

	});


	$('#nickname__save-button').on('click',function(){
		var name = $('#nickname__edit-input').val();
		getResults('/save-nick','json',{val: name}, function(res){
			if (res.val){
				//$('#nickname__title').html(name);
				$('#user__nickname-link').html(name);
				//$('#nickname__status').hide();
			}
		});
	});

	$('#nickname__edit-input').on('keyup', function(e){
		if (e.which==13){

		}
	});

	$('#email__save-button').on('click', function(){
				var val = $('#email__edit-input').val();

				if (!validateEmail(val)){
					$('#email__group').removeClass('has-success');
					$('#email__group').addClass('has-error');
					$('#email__status').html('<span style="color:red">Введите корректный адрес</span>');
					$('#email__status').show();
				} else {
					$('#email__group').removeClass('has-error');
					$('#email__group').addClass('has-success');
					$('#email__status').html('<span style="color:red">На указанный адрес отправлено письмо со ссылкой подтверждения</span>');
					getResults('/verify-email', 'json', {email:val}, function(res){

					});
				}
	});

	$('#website__save-button').on('click', function(){
				var val = $('#website__edit-input').val();

				if (!validateUrl(val)){
					$('#website__group').removeClass('has-success');
					$('#website__group').addClass('has-error');
					$('#website__status').html('<span style="color:red">Введите корректный адрес</span>');
					$('#website__status').show();
				} else {
					getResults('/save-info', 'json', {type: 'url', val: val}, function(res){
						if (res.status=='ok'){
							$('#website__group').removeClass('has-error');
							$('#website__group').addClass('has-success');
							$('#website__status').html('<span style="color:red">Адрес сайта успешно сохранён!</span>');	
						} else {
							alert ('error');
						}
					});
				}
	});

	$('#selfinfo__save-button').on('click', function(){
				var val = $('#selfinfo__edit-input').val();

				getResults('/save-info', 'json', {type: 'status', val: val}, function(res){
					if (res.status=='ok'){
						$('#selfinfo__group').removeClass('has-error');
						$('#selfinfo__group').addClass('has-success');
						$('#selfinfo__status').html('<span style="color:red">Ваш статус успешно сохранён!</span>');	
					} else {
						alert ('error');
					}
				});
				
	});



	$('.dropzone').dmUploader({
		url:'/avatar-upload',
		method:'POST',
		dataType:'json',
		onInit: function(){
		  console.log('Plugin successfully initialized');
		},
		onUploadSuccess: function(id, data){
			console.log(data.url);
			$('#avatar__image').hide(300);
			setTimeout(function(){
				$('#avatar__image').attr('src', data.url);
				$('#user__avatar').attr('src', data.url);
				$('#avatar__image').show(300);
			},350);

		}
	});




});