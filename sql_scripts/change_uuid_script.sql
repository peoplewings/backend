create or replace function change_to_uuid() returns void as
$$
declare
	l_tables character varying[];
	l_tab character varying[];
	i integer;
	l_rows refcursor;
	l_row record;
begin
	alter table notifications_accomodationinformation drop constraint notification_id_refs_id_149e5a78ad9a7fd0;
	alter table notifications_friendship drop constraint notifications_ptr_id_refs_id_f479b3132a2e9d8;
	alter table notifications_invites drop constraint notifications_ptr_id_refs_id_12b9f60d3c222e31;
	alter table notifications_invites drop constraint wing_id_refs_id_449f3420840f5195;
	alter table notifications_messages drop constraint notifications_ptr_id_refs_id_37a7935da0bcc96c;
	alter table notifications_notifications drop constraint first_sender_id_refs_id_443639816ee4311;
	alter table notifications_notifications drop constraint receiver_id_refs_id_443639816ee4311;
	alter table notifications_notifications drop constraint sender_id_refs_id_443639816ee4311;
	alter table notifications_notificationsalarm drop constraint receiver_id_refs_id_44864529a38ff72d;
	alter table notifications_requests drop constraint notifications_ptr_id_refs_id_7e7bd92b80c3338e;
	alter table notifications_requests drop constraint wing_id_refs_id_641199597a225b54;

	alter table wings_accomodation_public_transport drop constraint accomodation_id_refs_wing_ptr_id_56b7dbbc0be2eea8;
	alter table wings_accomodation_public_transport drop constraint publictransport_id_refs_id_27b3a6476407e252;
	alter table wings_accomodation drop constraint city_id_refs_id_18a3b66c56fd6c7;
	alter table wings_accomodation drop constraint wing_ptr_id_refs_id_f05c80b42cec567;
	alter table wings_wing drop constraint author_id_refs_id_23e59d851d7e03c1; 

	alter table cropper_cropped drop constraint cropper_cropped_original_id_fkey; 
	alter table cropper_original drop constraint cropper_original_owner_id_fkey;

	alter table people_reference drop constraint author_id_refs_id_5c9dd43ff8343326;
	alter table people_reference drop constraint commented_id_refs_id_5c9dd43ff8343326;
	alter table people_relationship drop constraint receiver_id_refs_id_67ff86d88ebfd514;
	alter table people_relationship drop constraint sender_id_refs_id_67ff86d88ebfd514;
	alter table people_userinstantmessage drop constraint people_userinstantmessage_instant_message_id_fkey;
	alter table people_userinstantmessage drop constraint user_profile_id_refs_id_18ce595;
	alter table people_userlanguage drop constraint people_userlanguage_language_id_fkey;
	alter table people_userlanguage drop constraint user_profile_id_refs_id_c29f14ab;
	alter table people_userprofile drop constraint current_city_id_refs_id_32301f0e99eca8db;
	alter table people_userprofile drop constraint hometown_id_refs_id_32301f0e99eca8db;
	alter table people_userprofile drop constraint last_login_id_refs_id_32301f0e99eca8db;
	alter table people_userprofile_interested_in drop constraint interests_id_refs_id_307299da86c82db8;
	alter table people_userprofile_interested_in drop constraint userprofile_id_refs_id_6a31859b7e0fc93f;
	alter table people_userprofile_other_locations drop constraint people_userprofile_other_locations_city_id_fkey;
	alter table people_userprofile_other_locations drop constraint userprofile_id_refs_id_4ab223b1;
	alter table people_userprofilestudieduniversity drop constraint people_userprofilestudieduniversity_university_id_fkey;
	alter table people_userprofilestudieduniversity drop constraint user_profile_id_refs_id_8b7f51ce;
	alter table people_usersocialnetwork drop constraint people_usersocialnetwork_social_network_id_fkey;
	alter table people_usersocialnetwork drop constraint user_profile_id_refs_id_e5bef669;

	alter table locations_region drop constraint country_id_refs_id_688446d03ef69106;
	alter table locations_city drop constraint region_id_refs_id_4877f50311a5997e;




------------------------------------------------------------------------------------------------
	l_tables := ARRAY['notifications_accomodationinformation', 'notifications_friendship', 'notifications_invites', 'notifications_messages', 'notifications_notifications', 'notifications_notificationsalarm', 'notifications_requests', 'wings_accomodation_public_transport', 
	'wings_publictransport', 'wings_accomodation', 'wings_wing', 'tastypie_apiaccess', 'tastypie_apikey', 'registration_registrationprofile', 'feedback_feedback', 'cropper_cropped', 'cropper_original', 'people_city', 'people_instantmessage', 'people_interests', 
	'people_language', 'people_reference', 'people_relationship', 'people_socialnetwork', 'people_university', 'people_userinstantmessage', 'people_userlanguage', 'people_userprofile', 'people_userprofile_interested_in', 'people_userprofile_other_locations', 
	'people_userprofilestudieduniversity', 'people_usersocialnetwork'];
	
	alter table notifications_accomodationinformation alter column id type character varying(36);
	alter table notifications_friendship alter column notifications_ptr_id type character varying(36);
	alter table notifications_invites alter column notifications_ptr_id type character varying(36);
	alter table notifications_messages alter column notifications_ptr_id type character varying(36);
	alter table notifications_notifications alter column id type character varying(36);
	alter table notifications_notificationsalarm alter column id type character varying(36);
	alter table notifications_requests alter column notifications_ptr_id type character varying(36);

	alter table wings_accomodation_public_transport alter column id type character varying(36); 
	alter table wings_publictransport alter column id type character varying(36); 
	alter table wings_wing alter column id type character varying(36);

	alter table tastypie_apiaccess alter column id type character varying(36);
	alter table tastypie_apikey alter column id type character varying(36);  

	alter table registration_registrationprofile alter column id type character varying(36);  

	alter table feedback_feedback alter column id type character varying(36); 

	alter table cropper_cropped alter column id type character varying(36); 
	alter table cropper_original alter column id type character varying(36);  

	alter table people_city alter column id type character varying(36);  
	alter table people_instantmessage alter column id type character varying(36);  
	alter table people_interests alter column id type character varying(36);  
	alter table people_language alter column id type character varying(36);  
	alter table people_reference alter column id type character varying(36);  
	alter table people_relationship alter column id type character varying(36);  
	alter table people_socialnetwork alter column id type character varying(36);  
	alter table people_university alter column id type character varying(36);  
	alter table people_userinstantmessage alter column id type character varying(36);  
	alter table people_userlanguage alter column id type character varying(36);  
	alter table people_userprofile alter column id type character varying(36);  
	alter table people_userprofile_interested_in alter column id type character varying(36);  
	alter table people_userprofile_other_locations alter column id type character varying(36);  
	alter table people_userprofilestudieduniversity alter column id type character varying(36);  
	alter table people_usersocialnetwork alter column id type character varying(36); 
	 
	alter table locations_city alter column id type character varying(36);
	alter table locations_country alter column id type character varying(36);
	alter table locations_region alter column id type character varying(36);

	
---------------------------------------------------------------------------------------------------------
	alter table cropper_cropped alter column original_id type character varying(36);
	alter table cropper_original alter column owner_id type character varying(36);
	alter table locations_city alter column region_id type character varying(36);
	alter table locations_region alter column country_id type character varying(36);
	alter table notifications_accomodationinformation alter column notification_id type character varying(36);
	alter table notifications_notifications alter column first_sender_id type character varying(36);
	alter table notifications_notifications alter column receiver_id type character varying(36);
	alter table notifications_notifications alter column sender_id type character varying(36);
	alter table notifications_notificationsalarm alter column receiver_id type character varying(36);
	alter table notifications_requests alter column wing_id type character varying(36);
	alter table notifications_invites alter column wing_id type character varying(36);
	alter table people_reference alter column author_id type character varying(36);
	alter table people_reference alter column commented_id type character varying(36);
	alter table people_relationship alter column sender_id type character varying(36);
	alter table people_relationship alter column receiver_id type character varying(36);
	alter table people_userinstantmessage alter column instant_message_id type character varying(36);
	alter table people_userinstantmessage alter column user_profile_id type character varying(36);
	alter table people_userlanguage alter column language_id type character varying(36);
	alter table people_userlanguage alter column user_profile_id type character varying(36);
	alter table people_userprofile alter column current_city_id type character varying(36);
	alter table people_userprofile alter column hometown_id type character varying(36);
	alter table people_userprofile alter column last_login_id type character varying(36);
	alter table people_userprofile_interested_in alter column interests_id type character varying(36);
	alter table people_userprofile_interested_in alter column userprofile_id type character varying(36);
	alter table people_userprofile_other_locations alter column city_id type character varying(36);
	alter table people_userprofile_other_locations alter column userprofile_id type character varying(36);
	alter table people_userprofilestudieduniversity alter column university_id type character varying(36);
	alter table people_userprofilestudieduniversity alter column user_profile_id type character varying(36);
	alter table people_usersocialnetwork alter column social_network_id type character varying(36);
	alter table people_usersocialnetwork alter column user_profile_id type character varying(36);
	alter table wings_accomodation alter column city_id type character varying(36);
	alter table wings_accomodation alter column wing_ptr_id type character varying(36);
	alter table wings_accomodation_public_transport alter column accomodation_id type character varying(36);
	alter table wings_accomodation_public_transport alter column publictransport_id type character varying(36);
	alter table wings_wing alter column author_id type character varying(36);

	------------------------------------------------------------------------------------------------

	alter table notifications_accomodationinformation add CONSTRAINT notification_id_refs_id_149e5a78ad9a7fd0 FOREIGN KEY (notification_id)
	      REFERENCES notifications_notifications (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table notifications_friendship add CONSTRAINT notifications_ptr_id_refs_id_f479b3132a2e9d8 FOREIGN KEY (notifications_ptr_id)
	      REFERENCES notifications_notifications (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table notifications_invites add CONSTRAINT notifications_ptr_id_refs_id_12b9f60d3c222e31 FOREIGN KEY (notifications_ptr_id)
	      REFERENCES notifications_notifications (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table notifications_invites add CONSTRAINT wing_id_refs_id_449f3420840f5195 FOREIGN KEY (wing_id)
	      REFERENCES wings_wing (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table notifications_messages add CONSTRAINT notifications_ptr_id_refs_id_37a7935da0bcc96c FOREIGN KEY (notifications_ptr_id)
	      REFERENCES notifications_notifications (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table notifications_notifications add CONSTRAINT first_sender_id_refs_id_443639816ee4311 FOREIGN KEY (first_sender_id)
	      REFERENCES people_userprofile (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table notifications_notifications add CONSTRAINT receiver_id_refs_id_443639816ee4311 FOREIGN KEY (receiver_id)
	      REFERENCES people_userprofile (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table notifications_notifications add CONSTRAINT sender_id_refs_id_443639816ee4311 FOREIGN KEY (sender_id)
	      REFERENCES people_userprofile (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table notifications_notificationsalarm add CONSTRAINT receiver_id_refs_id_44864529a38ff72d FOREIGN KEY (receiver_id)
	      REFERENCES people_userprofile (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table notifications_requests add CONSTRAINT notifications_ptr_id_refs_id_7e7bd92b80c3338e FOREIGN KEY (notifications_ptr_id)
	      REFERENCES notifications_notifications (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table notifications_requests add CONSTRAINT wing_id_refs_id_641199597a225b54 FOREIGN KEY (wing_id)
	      REFERENCES wings_wing (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;     

	alter table wings_accomodation_public_transport add CONSTRAINT accomodation_id_refs_wing_ptr_id_56b7dbbc0be2eea8 FOREIGN KEY (accomodation_id)
	      REFERENCES wings_accomodation (wing_ptr_id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table wings_accomodation_public_transport add CONSTRAINT publictransport_id_refs_id_27b3a6476407e252 FOREIGN KEY (publictransport_id)
	      REFERENCES wings_publictransport (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table wings_accomodation add CONSTRAINT city_id_refs_id_18a3b66c56fd6c7 FOREIGN KEY (city_id)
	      REFERENCES locations_city (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;     
	alter table wings_accomodation add CONSTRAINT wing_ptr_id_refs_id_f05c80b42cec567 FOREIGN KEY (wing_ptr_id)
	      REFERENCES wings_wing (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;  
	alter table wings_wing add CONSTRAINT author_id_refs_id_23e59d851d7e03c1 FOREIGN KEY (author_id)
	      REFERENCES people_userprofile (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;  

	alter table cropper_cropped add CONSTRAINT cropper_cropped_original_id_fkey FOREIGN KEY (original_id)
	      REFERENCES cropper_original (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table cropper_original add CONSTRAINT cropper_original_owner_id_fkey FOREIGN KEY (owner_id)
	      REFERENCES people_userprofile (id) MATCH SIMPLE
	      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;    


	alter table people_reference add CONSTRAINT author_id_refs_id_5c9dd43ff8343326 FOREIGN KEY (author_id)
		REFERENCES people_userprofile (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table people_reference add CONSTRAINT commented_id_refs_id_5c9dd43ff8343326 FOREIGN KEY (commented_id)
		REFERENCES people_userprofile (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table people_relationship add CONSTRAINT receiver_id_refs_id_67ff86d88ebfd514 FOREIGN KEY (receiver_id)
		REFERENCES people_userprofile (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table people_relationship add CONSTRAINT sender_id_refs_id_67ff86d88ebfd514 FOREIGN KEY (sender_id)
		REFERENCES people_userprofile (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table people_userinstantmessage add CONSTRAINT people_userinstantmessage_instant_message_id_fkey FOREIGN KEY (instant_message_id)
		REFERENCES people_instantmessage (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table people_userinstantmessage add CONSTRAINT user_profile_id_refs_id_18ce595 FOREIGN KEY (user_profile_id)
		REFERENCES people_userprofile (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table people_userlanguage add CONSTRAINT people_userlanguage_language_id_fkey FOREIGN KEY (language_id)
		REFERENCES people_language (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table people_userlanguage add CONSTRAINT user_profile_id_refs_id_c29f14ab FOREIGN KEY (user_profile_id)
		REFERENCES people_userprofile (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table people_userprofile add CONSTRAINT current_city_id_refs_id_32301f0e99eca8db FOREIGN KEY (current_city_id)
		REFERENCES locations_city (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table people_userprofile add CONSTRAINT hometown_id_refs_id_32301f0e99eca8db FOREIGN KEY (hometown_id)
		REFERENCES locations_city (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table people_userprofile add CONSTRAINT last_login_id_refs_id_32301f0e99eca8db FOREIGN KEY (last_login_id)
		REFERENCES locations_city (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED; 
	alter table people_userprofile_interested_in add CONSTRAINT interests_id_refs_id_307299da86c82db8 FOREIGN KEY (interests_id)
		REFERENCES people_interests (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table people_userprofile_interested_in add CONSTRAINT userprofile_id_refs_id_6a31859b7e0fc93f FOREIGN KEY (userprofile_id)
		REFERENCES people_userprofile (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED; 
	alter table people_userprofile_other_locations add CONSTRAINT people_userprofile_other_locations_city_id_fkey FOREIGN KEY (city_id)
		REFERENCES people_city (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table people_userprofile_other_locations add CONSTRAINT userprofile_id_refs_id_4ab223b1 FOREIGN KEY (userprofile_id)
		REFERENCES people_userprofile (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table people_userprofilestudieduniversity add CONSTRAINT people_userprofilestudieduniversity_university_id_fkey FOREIGN KEY (university_id)
		REFERENCES people_university (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table people_userprofilestudieduniversity add CONSTRAINT user_profile_id_refs_id_8b7f51ce FOREIGN KEY (user_profile_id)
		REFERENCES people_userprofile (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;   
	alter table people_usersocialnetwork add CONSTRAINT people_usersocialnetwork_social_network_id_fkey FOREIGN KEY (social_network_id)
		REFERENCES people_socialnetwork (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table people_usersocialnetwork add CONSTRAINT user_profile_id_refs_id_e5bef669 FOREIGN KEY (user_profile_id)
		REFERENCES people_userprofile (id) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;    

	alter table locations_city add CONSTRAINT region_id_refs_id_4877f50311a5997e FOREIGN KEY (region_id)
		REFERENCES locations_region (id) MATCH SIMPLE
		ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
	alter table locations_region add CONSTRAINT country_id_refs_id_688446d03ef69106 FOREIGN KEY (country_id)
		REFERENCES locations_country (id) MATCH SIMPLE
		ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

	FOR i IN array_lower(l_tables, 1) .. array_upper(l_tables, 1) loop
		open l_rows for execute 'select * from '||l_tables[i]||'';
		raise notice '%', (SELECT pg_attribute.attname, format_type(pg_attribute.atttypid, pg_attribute.atttypmod) FROM pg_index, pg_class, pg_attribute WHERE pg_class.oid = 'TABLENAME'::regclass AND indrelid = pg_class.oid AND pg_attribute.attrelid = pg_class.oid AND pg_attribute.attnum = any(pg_index.indkey) AND indisprimary);
		fetch l_rows into l_row;
		while found loop
			raise notice '%', l_tables[i];
			execute 'update '||l_tables[i]||' set id = '''||cast((select uuid_generate_v4()) as character varying(36))||''' where id ilike '''||l_row.id||'''';
			---raise notice '%s', l_row;
			fetch l_rows into l_row;
		end loop;
		close l_rows;
	end loop;
	
raise exception 'lol';
end;
$$ language 'plpgsql' volatile;
select * from change_to_uuid()
