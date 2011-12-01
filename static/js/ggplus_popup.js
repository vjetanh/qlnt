/**
 * googleplus popup is similar to Google Plus circle choices pop up except that
 * you can apply googleplus popup to an existed input like combobox.
 * googleplus popup r1 // 2011.11.26 // jQuery 1.5.1+
 *
 * googleplus popup is currently available for use in all personal or commercial
 * projects under both MIT and GPL licenses. This means that you can choose
 * the license that best suits your project, and use it accordingly.
 *
 *
 * @param popupWindow // a div that will be popped up
 * @param init // a callback function that will be triggered before pop up appears
 * @param callback // a callback function that handle close popup event
 *        callback function will receive two objects, one is jquery event(mouse leave), other is the div popped up
 * @param live // boolean parameter
 *        if this parameter is true, the change of the pop up div will make the original input changed, it will
 *        trigger input change event before call callback function
 * @author vutran at University of Engineering and Technology, VNU, VN
 */

(function($){
    $.fn.googlePlusPopup = function( popupWindow, init, callback){
        // normalize params
        var live = true;
        var emptySelectValue = false;
        init = (init && typeof(init)==="function")?(init): function(){};
        callback = (callback && typeof(callback)==="function")?(callback): function(){};
        // end normalize
        var self = this;
        var oldValue;
        var autoCreatePopup = false;
        // get default popup div base on the input context,
        // this should apply some js listener for convenience
        // these inputs are provided:
        // - select
        var getPopupDiv = function(ob){
            // for select
            if (ob.is('select')){
                var result= jQuery('<div/>',{
                    class: "googlePlusPopupDiv googlePlusPopupShadow",
                    css: {
                        display: "none"
                    }
                });
                ob.find('option').each(function(){
                    var option = $(this);
                    var name = (option.attr('name'))?(ob.attr('name')):('popupSelect'+ob.attr('id'));
                    var id = (name + option.attr('value')).replace(/ /g,'');
                    var radioBox = jQuery('<input type="radio"/>').attr(
                            {
                                name: name,
                                id: id,
                                value: option.attr('value')
                                
                            }
                    ).css('margin-right', '10px').click(function(e){
                                if ($(this).prop('checked') && emptySelectValue)
                                    $(this).prop('checked', false);
                                else
                                    console.log('clicked input '+ $(this).attr('id'));
                                    $(this).prop('checked', true);
                                return true;
                            });
                    if (option.attr('selected') == 'selected'){
                        oldValue = option.attr('value');
                        radioBox.prop('checked', true);
                    }
                    var newOptionDiv = jQuery('<div/>',{
                        html: radioBox,
                        //'<input type="radio" name="'+name+'" value="'+ option.attr('value')+'" />' + option.text(),
                        class: 'popupSelectOption',
                        click: function(e){
                            if ($("#"+id).prop('checked') && emptySelectValue)
                                $("#"+id).prop('checked', false);
                            else
                                console.log('clicked div' + "#"+id);
                                $("#"+id).prop('checked', true);
                            return true;
                        }
                    });

                    newOptionDiv.append(option.text());
                    result.append(newOptionDiv);

                });

                console.log(result.height());

                return result;
            }
        };

        var getValue = function(ob){
            if (ob.is('select')){
                return ob.find('option:selected').text();
            }
        };
        var applyValue = function(popup, original){
            if (original.is('select')){
                var newValue = popup.find('input:checked').val();
                original.val(newValue);
                if (newValue != oldValue)
                    original.trigger('change');
            }
        };
        if (!popupWindow){
            // auto create popup window base on the input context
            autoCreatePopup = true;
        }

        // insert before this with a button
        var width = this.outerWidth();
        var height= this.outerHeight();
        var button = jQuery('<button/>',
                {
                    class: 'googlePlusPopupButton',
                    text: getValue(this),
                    css: {
                        width: width,
                        height: height
                    }
                }
        );
        // apply hover function
        button.bind('mouseenter', function(e){
            ev = jQuery.extend({},e);
            init.apply(this,[ev]);
            var top = button.offset().top;
            var left= button.offset().left;
            if (autoCreatePopup){
                popupWindow = getPopupDiv(self);
                $(".googlePlusPopupDiv").each(function(){
                    $(this).trigger('mouseleave');
                });
                popupWindow.insertAfter(button);
            }
            popupWindow.css({
                'top': top,
                'left': left,
                'min-width': width,
                'position':'absolute',
                'z-index': '2000'
            });
            popupWindow.bind('mouseleave',function(e){
                ev = jQuery.extend({}, e);
                popupWindow.fadeOut(400);
                if (live){
                    applyValue(popupWindow, self);
                    button.text(getValue(self));
                }
                if (autoCreatePopup)
                    popupWindow.remove();
                callback.apply(this,[ev, popupWindow]);
            });

            popupWindow.fadeIn(200);
        });
        //this.replaceWith(button);
        this.hide();
        button.insertAfter(this);
        return button;
    }
})(jQuery);