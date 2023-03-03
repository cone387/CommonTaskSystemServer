$(document).ready(function () {
  const $scheduleType = $('#id_schedule_type');
  const $crontab = $('.form-row.field-crontab');
  const $onceSchedule = $('.form-row.field-once_schedule')
  const $periodSchedule = $('.form-row.field-period_schedule');

  const $timingsDiv = $("div[class*='timing']");
  const $timingType = $('#id_timings_type');
  const $timingTime = $('.form-row.field-timing_time');
  const $timingWeekdays = $('.form-row.field-weekdays');


  function show_hide_timing_fields(){
    const timingType = $timingType.val();
    const $periodUnit = $('#id_period_unit');
    if(timingType === "DATETIMES"){
      $timingWeekdays.hide();
      $periodUnit.hide();
      $timingTime.hide();
      return;
    }
    $periodUnit.show();
    $timingTime.show();
    if(timingType === 'DAYS'){
      $timingWeekdays.hide();
      $periodUnit.text('天');
    }
    if(timingType === 'WEEKDAYS'){
      $timingWeekdays.show();
      $periodUnit.text('周');
    }else if(timingType === "MONTH"){
      $timingWeekdays.hide();
      $periodUnit.text('月');
    }
  }

  function show_hide_timings(show){
    if(show){
      $timingsDiv.show();
      show_hide_timing_fields();
    }else{
      $timingsDiv.hide();
    }
  }

  function show_hide_fields() {
    console.log($scheduleType.val());
    const scheduleType = $scheduleType.val();
    if (scheduleType === 'C') {
      $crontab.show();
      $onceSchedule.hide();
      $periodSchedule.hide();
    } else if (scheduleType === 'S') {
      $crontab.hide();
      $onceSchedule.hide();
      $periodSchedule.show();
    } else if (scheduleType === 'O') {
      $crontab.hide();
      $onceSchedule.show();
      $periodSchedule.hide();
    }else if(scheduleType === 'T'){
      $crontab.hide();
      $onceSchedule.hide();
      $periodSchedule.hide();
    }
    show_hide_timings(scheduleType === 'T');
  }
  show_hide_fields();
  $scheduleType.on('change', show_hide_fields);
  $timingType.on('change', show_hide_timing_fields);
});