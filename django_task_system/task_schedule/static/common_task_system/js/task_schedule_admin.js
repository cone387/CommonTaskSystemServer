$(document).ready(function () {
  const $type = $('#id_type');
  const $crontab = $('.form-row.field-crontab');
  const $nextScheduleTime = $('.fieldBox.field-next_schedule_time');
  const $period = $('.fieldBox.field-period');
  const $timings = $('.form-row.field-timings');

  function show_hide_fields() {
    console.log($type.val());
    if ($type.val() === 'C') {
      $crontab.show();
      $nextScheduleTime.hide();
      $period.hide();
      $timings.hide();
    } else if ($type.val() === 'S') {
      $crontab.hide();
      $nextScheduleTime.show();
      $period.show();
      $timings.hide();
    } else if ($type.val() === 'O') {
      $crontab.hide();
      $nextScheduleTime.show();
      $period.hide();
      $timings.hide();
    }else if($type.val() === 'T'){
      $crontab.hide();
      $nextScheduleTime.hide();
      $period.hide();
      $timings.show();
    }
  }
  show_hide_fields();
  $type.on('change', show_hide_fields);
});