with queries as (
    select sum(running_time) query_time,
           count(*) as runs,
          pulse_id, pulse.name as pulse_name
    from query_execution
        inner join report_card card
            on query_execution.card_id = card.id
        left outer join pulse on query_execution.pulse_id = pulse.id
    where started_at > current_timestamp - interval '30 days'
      and card.database_id = 6
    group by 3, 4
)
select row_number() over(order by proportion desc) rank,
       proportion,
       sum(proportion) over(order by proportion desc rows between unbounded preceding and current row) as cum_proportion,
       runs, query_time, total_time,
       pulse_id, pulse_name
from (
    select query_time / sum(query_time) over() as proportion,
           runs,
           query_time,
           sum(query_time) over() as total_time,
           pulse_id, pulse_name
    from queries) as query_proportions
order by 2 desc;
