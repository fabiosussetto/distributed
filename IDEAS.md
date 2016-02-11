# Description

* Services expose resources (like in REST). Resources are named and namespaced with the service id
  (e.g. fs:auth:user, format org:service_id:resource_name).
  
* Services emit events when resources change for CRUD operations. E.g. fs:auth:user:deleted, fs:auth:user:updated.
  These events payloads contain the data relative to that resource.
  
* Services should expose a set of RPC calls to operate on their entities.
  To ask a list of users, another service should broadcast a message on the RPC exchange such as:
  Get user detail: { to: fs:auth, method: GET, uri: '/user/user_id' }
  Get list of users: { to: fs:auth, method: GET, uri: '/user', params: { limit: 50, active: true } }
  Update user: { to: fs:auth, method: PUT, uri: '/user/user_id', data: { username: john } }
  
  Implementation ref: https://www.rabbitmq.com/direct-reply-to.html
 

# Resource mapping

newsletter_subscriber: id | subscribed_on | active | user > user:user_id (resource FK)

blog_post: id | title | content | author > user:user_id (resource FK)
 
resource map:
 user -> fs:auth:user
 

# Exposed resources definition

### Example:

entity_map:
  user: sd:auth:user
  email: fb:mailer:mail
  newsletter: sd:mailcampaign:newsletter  

sd:auth:
 - entities:
     user:
       - username
       - email
       - active
       - registered_on       


sd:mailcampaign:
 - entities:
     subscriber:
       - subscribed_on
       - user [user]
       - active
     newsletter:
       - title
       - content  
       
fb:mailer:
 - entities:
     email:
       - to_user [user]
       - newsletter [newsletter]
       - sent_on
       - retries_count       
