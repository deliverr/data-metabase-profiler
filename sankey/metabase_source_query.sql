-- source query against Metabase postgresql database
select count(*) as runs,
       card_id, card.name as card_name,
       executor_id as user_id,
       u.first_name as first_name
from query_execution query
inner join report_card card on query.card_id  = card.id
inner join core_user u on query.executor_id = u.id
where query.database_id = 6 and query.started_at > current_timestamp - interval '30 days'
group by card_id, name, user_id, first_name
order by runs desc;
