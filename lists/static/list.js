window.Superlists = {};
window.Superlists.initialize = function () {
    $('input[name="text"]').on('keypress', function() {
        console.log('hiding validation error');
        $('.has-error').hide();
    });
};
