create or replace function change_wing_city() returns void as
$$
declare
	l_i record;
begin
	alter table wings_wing add column city_id integer;
	for l_i in select * from wings_accomodation loop
		update wings_wing set city_id = l_i.city_id where id = l_i.wing_ptr_id;
	end loop;
	alter table wings_wing add CONSTRAINT city_id_refs_id_18a3b66c56fd6c7 FOREIGN KEY (city_id) REFERENCES locations_city (id) MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table wings_wing alter column city_id set not null;

	alter table wings_accomodation drop column city_id;
end;
$$ language 'plpgsql' volatile;
select * from change_wing_city();