-- source query against Metabase postgresql database
with queries as (
    select sum(running_time) query_time, card_id, card.name as card_name,
           count(*) as runs, core_user.first_name, core_user.last_name, card.creator_id
    from query_execution
        inner join report_card card
            on query_execution.card_id = card.id
        left outer join core_user
            on card.creator_id = core_user.id
    where started_at > current_timestamp - interval '{{days_back}} days'
      and card.database_id = 6
    group by 2, 3, 5, 6, 7
)
select row_number() over(order by proportion desc) rank,
       proportion,
       sum(proportion) over(order by proportion desc rows between unbounded preceding and current row) as cum_proportion,
       card_id, card_name, runs, query_time, total_time,
       first_name, last_name, creator_id
from (
    select query_time / sum(query_time) over() as proportion,
           card_id, card_name, runs,
           query_time,
           sum(query_time) over() as total_time,
           first_name, last_name, creator_id
    from queries) as query_proportions
order by 2 desc;
