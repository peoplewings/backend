create or replace function create_terms_and_conditions() returns void as
$$
declare

begin
	create table registration_termsandconditions(
		id serial not null,
		user_id integer,
		email character varying not null,
		registration_date bigint not null,
		deletion_date bigint,
		has_accepted boolean not null,
		constraint registration_termsandconditions_pkey primary key (id),
		constraint user_id_refs_id_69142f3d11f7cede foreign key (user_id) references auth_user (id) match simple on update no action on delete set null deferrable initially deferred);
		
end;
$$
language 'plpgsql' volatile;
select * from create_terms_and_conditions()