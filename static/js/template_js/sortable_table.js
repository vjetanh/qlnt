/**
 * Created by PyCharm.
 * User: vutran
 * Date: 7/29/11
 * Time: 7:00 AM
 * To change this template use File | Settings | File Templates.
 */

$(document).ready(function(){
            $("#guide").hide();
            $("#guide").click(function(){
                return false;
            });
            function isSorting(){
                return $("#sort").val() != "Sắp xếp";
            }

            $("td > input[type=text]").each(function(){
                $(this).click(function(){
                    return false;
                })
            });

            $("td > select").each(function(){
                $(this).click(function(){
                    return false;
                })
            });

            $(document).keydown(function(event){
                if (isSorting()){
                    var theSelected = $(".selected");
                    if (theSelected.length >0 ){
                        if (event.which == 38){
                            // if key is up arrow
                            var prev = theSelected.prev('tr.sortable');
                            if (prev.length > 0){
                                var oldIndex = theSelected.children('td.index').children('p');
                                var newIndex = prev.children('td.index').children('p');
                                var temp = oldIndex.text();
                                oldIndex.text(newIndex.text());
                                newIndex.text(temp);
                                prev.before(theSelected);
                            }
                        } else if (event.which == 40){
                            // if key is down arrow
                            var next = theSelected.next('tr.sortable');
                            if (next.length>0){
                                var oldIndex = theSelected.children('td.index').children('p');
                                var newIndex = next.children('td.index').children('p');
                                var temp = oldIndex.text();
                                oldIndex.text(newIndex.text());
                                newIndex.text(temp);
                                next.after(theSelected);
                            }
                        } else if (event.which == 13){
                            theSelected.removeClass('selected');
                            theSelected.children('.index').children('span').hide();
                        }
                    } else {
                        var theFocused = $(".focused");
                        if (event.which == 38){
                            // if key is up arrow
                            var prev = theFocused.prev('tr.sortable');
                            if (prev.length > 0){
                                prev.addClass('focused');
                                theFocused.removeClass('focused');
                            }
                        } else if (event.which == 40){
                            // if key is down arrow
                            var next = theFocused.next('tr.sortable');
                            if (next.length>0){
                                next.addClass('focused');
                                theFocused.removeClass('focused');
                            }
                        } else if (event.which == 13){
                            theFocused.addClass('selected');
                            theFocused.children('.index').children('span').show();
                        }
                    }
                }
            });
            $(".sortable").each(function(){
                $(this).click(function(){
                    if ( isSorting()){
                        if ($(this).hasClass('selected')){
                            $(this).removeClass('selected');
                            $(this).children('.index').children('span').hide();
                        } else {
                            $(".selected").each(function(){
                                $(this).removeClass('selected');
                                $(this).children('.index').children('span').hide();
                            });
                            $(".focused").each(function(){
                                $(this).removeClass('focused');
                                $(this).children('.index').children('span').hide();
                            });

                            $(this).addClass('focused selected');
                            $(this).children('.index').children('span').show();

                        }
                    }
                })
            });


            $("#sort").click(function(){
               // create extra buttons and icons.
                var firstFocus = $("tr:eq(1)");
                if ($("#sort").val() == "Sắp xếp"){
                    $("#sort").after("&nbsp <input id='cancel' type='button' value='Hủy sắp xếp'/>");
                    $("#guide").show();
                    $("#subject_form").hide();
                    $("#cancel").click(function(){
                        document.location.replace($("#redirect_link").text());
                    });
                    $("#sort").val("Lưu thứ tự");
                    firstFocus.addClass('focused');
                } else {
                // save the indexes to db
                    var data='';
                    $("tr.sortable").each(function(){
                        var id = $(this).attr('id');
                        var index = $(this).children('td.index').children('p').text();
                        data = data + id + '_' + index + '/';
                    });

                    var arg = { type:"POST",
                        url: $("#ajax_to").text(),
                        data:{data: data},
                        datatype:"json",
                        success: function(){
                            // restore original state of table
                            $("#alphabet").remove();
                            $("#cancel").remove();
                            $("#guide").hide();
                            $("#subject_form").show();
                            $("#sort").val("Sắp xếp");
                            $("span.ui-icon ui-icon-arrowthick-2-n-s").each(function(){
                                $(this).hide();
                            });
                            $(".selected").removeClass('selected');
                            $(".focused").removeClass('focused');
                        }
                    };
                    $.ajax(arg);
                }
                return false;
            });
});

