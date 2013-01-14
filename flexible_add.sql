create or replace function flexible_add() returns void as
$$
declare

begin
	alter table notifications_accomodationinformation add column flexible_start boolean default false;
	alter table notifications_accomodationinformation add column flexible_end boolean default false;
end;
$$
language 'plpgsql' volatile;
select * from flexible_add();