alter table notifications_notificationsalarm drop column created;
alter table notifications_notificationsalarm add column created bigint default 0;
alter table people_userprofile add column reply_rate integer default 0;
alter table people_userprofile add column reply_time bigint default 0;
create or replace function batch_reply_rate() returns integer as
$$
declare
	l_profiles record;
	l_notifs record;
	l_n_notifs integer;
	l_n_replied_notifs float;
	l_n_time integer;
	l_created bigint;
begin
	for l_profiles in select * from people_userprofile loop
		l_n_notifs := 0;
		l_n_replied_notifs := 0;
		l_n_time := 0;
		for l_notifs in select "reference", min(created) as min_created from notifications_notifications where kind in ('request', 'invite') and receiver_id = l_profiles.id and first_sender_id != l_profiles.id group by "reference" loop
			perform * from notifications_notifications where "reference" = l_notifs.reference and sender_id = l_profiles.id;
			if found then
				l_n_replied_notifs := l_n_replied_notifs + 1;
				select min(created) into l_created from notifications_notifications where "reference" = l_notifs.reference and sender_id = l_profiles.id;
				l_n_time := l_n_time + (l_created - l_notifs.min_created);
			end if;
			l_n_notifs := l_n_notifs + 1;
		end loop;
		if l_n_notifs != 0 then
			update people_userprofile set reply_rate = cast(((l_n_replied_notifs/l_n_notifs) * 100) as integer) where id = l_profiles.id;
		else
			update people_userprofile set reply_rate = -1 where id = l_profiles.id;
		end if;
		if l_n_notifs != 0 and l_n_replied_notifs != 0 then
			update people_userprofile set reply_time = (l_n_time/l_n_replied_notifs) where id = l_profiles.id;
		else
			update people_userprofile set reply_time = -1 where id = l_profiles.id;
		end if;
	end loop;
	return 1;	
end;
$$
language 'plpgsql' volatile;

select * from batch_reply_rate()