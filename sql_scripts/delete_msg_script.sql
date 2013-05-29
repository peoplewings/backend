create or replace function delete_msg_script() returns void as
$$
declare
	
begin
	alter table notifications_notifications add column first_sender_visible boolean default true;
	alter table notifications_notifications add column second_sender_visible boolean default true;
end;
$$
language 'plpgsql' volatile;
select * from delete_msg_script()