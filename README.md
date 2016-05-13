# busad
Event:          'add_group'
Direction:      Client to Server
Description:
Data Format:
{
    cmd     :   'add_group';
    name    :   string;
    group_addr  :string;                // group addr, 8 hex digits (without dashes)
    nwkskey     :string;                // nwkskey, 16 hex digits (without dashes)
    appskey?    :string;
}

Event:          'add_group'
Direction:      Server to Client
Description:
Data Format:
{
    cmd     :   'add_group';
    group_addr?:string;                 // group addr, 8 hex digits (without dashes)
    group_id?:  string;                 // group id, 8 hex digits (without dashes)
    success :   0 or 1;
    error?  :   string;
}

Event:          'add_dev_into_group'
Direction:      Client to Server
Description:
Data Format:
{
    cmd     :   'add_dev_into_group';
    group_id:   string;                 // group id, 8 hex digits (without dashes)
    dev_eui:    string;                 // device EUI, 16 hex digits (without dashes)
}

Event:          'add_dev_into_group'
Direction:      Server to Client
Description:
Data Format:
{
    cmd     :   'add_dev_into_group';
    group_id?:  string;                 // group id, 8 hex digits (without dashes)
    success :   0 or 1;                 // device EUI, 16 hex digits (without dashes)
    error?  :   string;
}

Event:          'rm_dev_from_group'
Direction:      Client to Server
Description:
Data Format:
{
    cmd     :   'rm_dev_from_group';
    group_id:   string;                 // group id, 8 hex digits (without dashes)
    dev_eui:    string;                 // device EUI, 16 hex digits (without dashes)
}

Event:          'rm_dev_from_group'
Direction:      Server to Client
Description:
Data Format:
{
    cmd     :   'rm_dev_from_group';
    group_id?:  string;                 // group id, 8 hex digits (without dashes)
    dev_eui? :   string;
    success :   0 or 1;                 // device EUI, 16 hex digits (without dashes)
    error?  :   string;
}
