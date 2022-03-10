## Redis

Redis is an in-memory data structure storage, used as a distributed, in-memory key-value database, cache and message broker, with optional durability. Redis supports various types of abstract data structures, such as strings, lists, maps, sets, ...

Redis is a system that can be considered at the same time a store and a cache, using a design where data is always modified and read from the main computer memory, but also stored on disk in a format that is unsuitable for random access of data, but only to reconstruct the data back in memory once the system restarts. At the same time, Redis provides a data model that is very unusual compared to a relational database management system (RDBMS), read MySQL, MYSQL forks, ... Because Redis is key-value oriented, data is stored in a manner suitable for quick retrieval later, without assistance from the database system in the form of secondary indexes, aggregations or other common features of traditional RDBMS, e.g. Join functions in SQL, which causes delayed response times.

All Redis data resides in memory, which enables low latency and high throughput data access. Unlike traditional databases, In-memory data stores don’t require a trip to disk, reducing engine latency to microseconds. Because of this, in-memory data stores can support an order of magnitude more operations and faster response times. The result is blazing-fast performance with average read and write operations taking less than a millisecond and support for millions of operations per second.

Redis is a great choice for implementing a highly available in-memory cache to decrease data access latency, increase throughput, and ease the load off a relational or NoSQL database and application. Redis can serve frequently requested items at sub-millisecond response times.

In this case, because time series data is used, a RedisTimeSeries database is utilized, which is a module that adds a time series data structure to Redis.

Since the rule-based control is done in real-time, it is clear that the use of Redis has a very large impact on passing the input data to the control strategy software. Because the latency of reading the data and control should be minimized, the use of Redis is preferred over other time series databases, for example, InfluxDB.