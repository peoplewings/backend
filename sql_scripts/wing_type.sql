create or replace function insert_wing_type() returns void as
$$
declare
	l_rec record;
begin
	alter table wings_wing add column wing_type character varying(100) NOT NULL DEFAULT ''::character varying;
end;
$$
language 'plpgsql' volatile;
select * from insert_wing_type();